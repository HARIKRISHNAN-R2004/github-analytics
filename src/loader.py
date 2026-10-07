import os
import sys
import pandas as pd
from typing import Dict
from sqlalchemy.orm import Session

# Ensure project root is in sys.path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config
from src.database import db_manager, Repository, RepositoryMetrics, LanguageStats, RepositoryTopics


class GitHubLoader:
    """Loader component for persisting transformed DataFrames into target database tables."""

    def __init__(self, db=None):
        self.db = db or db_manager

    def load_repositories(self, df_repos: pd.DataFrame, session: Session) -> int:
        """
        Loads master repository records with UPSERT (Insert or Update) logic.
        """
        if df_repos.empty:
            return 0

        inserted_or_updated = 0
        for _, row in df_repos.iterrows():
            repo_id = int(row["repo_id"])
            existing_repo = session.query(Repository).filter_by(repo_id=repo_id).first()

            if existing_repo:
                # Update master record fields
                existing_repo.owner = row["owner"]
                existing_repo.repo_name = row["repo_name"]
                existing_repo.full_name = row["full_name"]
                existing_repo.url = row["url"]
                existing_repo.description = row["description"]
                existing_repo.primary_language = row["primary_language"]
                existing_repo.last_updated = row["last_updated"]
                existing_repo.fetched_date = row["fetched_date"]
            else:
                # Insert new master record
                new_repo = Repository(
                    repo_id=repo_id,
                    owner=row["owner"],
                    repo_name=row["repo_name"],
                    full_name=row["full_name"],
                    url=row["url"],
                    description=row["description"],
                    primary_language=row["primary_language"],
                    created_at=row["created_at"],
                    last_updated=row["last_updated"],
                    fetched_date=row["fetched_date"],
                )
                session.add(new_repo)
            inserted_or_updated += 1

        return inserted_or_updated

    def load_metrics(self, df_metrics: pd.DataFrame, session: Session) -> int:
        """Loads time-series daily snapshot metrics (Append-only)."""
        if df_metrics.empty:
            return 0

        metrics_objs = [
            RepositoryMetrics(
                repo_id=int(row["repo_id"]),
                stars_count=int(row["stars_count"]),
                forks_count=int(row["forks_count"]),
                watchers_count=int(row["watchers_count"]),
                open_issues=int(row["open_issues"]),
                fetched_date=row["fetched_date"],
            )
            for _, row in df_metrics.iterrows()
        ]
        session.bulk_save_objects(metrics_objs)
        return len(metrics_objs)

    def load_languages(self, df_langs: pd.DataFrame, session: Session) -> int:
        """Loads language byte percentage breakdown."""
        if df_langs.empty:
            return 0

        lang_objs = [
            LanguageStats(
                repo_id=int(row["repo_id"]),
                language=str(row["language"]),
                bytes=int(row["bytes"]),
                percentage=float(row["percentage"]),
                fetched_date=row["fetched_date"],
            )
            for _, row in df_langs.iterrows()
        ]
        session.bulk_save_objects(lang_objs)
        return len(lang_objs)

    def load_topics(self, df_topics: pd.DataFrame, session: Session) -> int:
        """Loads repository topic tags."""
        if df_topics.empty:
            return 0

        topic_objs = [
            RepositoryTopics(
                repo_id=int(row["repo_id"]),
                topic=str(row["topic"]),
                fetched_date=row["fetched_date"],
            )
            for _, row in df_topics.iterrows()
        ]
        session.bulk_save_objects(topic_objs)
        return len(topic_objs)

    def load_all(self, transformed_dfs: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """
        Executes complete load pipeline inside a single transactional database session.
        Guarantees ACID compliance (Rolls back automatically on failure).
        """
        print(f"\n[START] Starting Database Load Phase...")
        session = self.db.get_session()
        counts = {}

        try:
            # 1. Initialize schema tables if not exist
            self.db.init_db()

            # 2. Load Master Repositories
            counts["repositories"] = self.load_repositories(transformed_dfs["repositories"], session)
            
            # 3. Load Fact & Dimension Tables
            counts["metrics"] = self.load_metrics(transformed_dfs["metrics"], session)
            counts["languages"] = self.load_languages(transformed_dfs["languages"], session)
            counts["topics"] = self.load_topics(transformed_dfs["topics"], session)

            # Commit Transaction
            session.commit()
            print("[SUCCESS] Load Phase Completed and Committed to Database:")
            print(f"  - Repositories Processed: {counts['repositories']}")
            print(f"  - Metrics Snapshot Rows: {counts['metrics']}")
            print(f"  - Language Breakdown Rows:{counts['languages']}")
            print(f"  - Topics Tag Rows:       {counts['topics']}")
            return counts

        except Exception as e:
            session.rollback()
            print(f"[ERROR] Transaction failed! Rolled back changes. Details: {e}")
            raise e
        finally:
            session.close()


if __name__ == "__main__":
    from src.extractor import GitHubExtractor
    from src.transformer import GitHubTransformer

    print("==========================================")
    print("        STEP 5 LOADER TEST               ")
    print("==========================================")

    # 1. Extract sample
    extractor = GitHubExtractor()
    raw_data = extractor.extract_all(target_languages=["Python"], max_per_lang=2)

    # 2. Transform sample
    transformer = GitHubTransformer()
    dfs = transformer.transform_all(raw_data)

    # 3. Load into database
    loader = GitHubLoader()
    load_counts = loader.load_all(dfs)

    print("\nSUCCESS: Step 5 Loader executed cleanly!")
