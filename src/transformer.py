import os
import sys
from datetime import datetime, date
import pandas as pd
from typing import List, Dict, Any

# Ensure project root is in sys.path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config


class GitHubTransformer:
    """Transformer component for cleaning, validating, and normalizing raw API data."""

    def __init__(self):
        self.today = date.today()

    def parse_datetime(self, date_str: str) -> datetime:
        """Parse ISO 8601 timestamp string into datetime object."""
        if not date_str:
            return None
        try:
            # Python standard library ISO 8601 parser
            cleaned_str = str(date_str).replace("Z", "+00:00")
            return datetime.fromisoformat(cleaned_str)
        except Exception:
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                return None

    def transform_all(self, raw_repos: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
        """
        Transforms a list of raw GitHub API objects into 4 clean Pandas DataFrames:
        1. repositories
        2. repository_metrics
        3. language_stats
        4. repository_topics
        """
        repos_list = []
        metrics_list = []
        langs_list = []
        topics_list = []

        print(f"\n[START] Starting Transformation Phase for {len(raw_repos)} raw repositories...")

        for repo in raw_repos:
            repo_id = repo.get("id")
            if not repo_id:
                continue

            owner = repo.get("owner", {}).get("login", "unknown")
            repo_name = repo.get("name", "")
            full_name = repo.get("full_name", f"{owner}/{repo_name}")
            url = repo.get("html_url", "")
            description = repo.get("description") or ""
            description = str(description)[:500]  # Truncate long descriptions
            primary_lang = repo.get("language") or "Other"

            created_at = self.parse_datetime(repo.get("created_at"))
            last_updated = self.parse_datetime(repo.get("updated_at"))

            # 1. Master Repository Row
            repos_list.append({
                "repo_id": repo_id,
                "owner": owner,
                "repo_name": repo_name,
                "full_name": full_name,
                "url": url,
                "description": description,
                "primary_language": primary_lang,
                "created_at": created_at,
                "last_updated": last_updated,
                "fetched_date": self.today,
            })

            # 2. Time-Series Metrics Row
            metrics_list.append({
                "repo_id": repo_id,
                "stars_count": int(repo.get("stargazers_count", 0)),
                "forks_count": int(repo.get("forks_count", 0)),
                "watchers_count": int(repo.get("watchers_count", 0)),
                "open_issues": int(repo.get("open_issues_count", 0)),
                "fetched_date": self.today,
            })

            # 3. Language Breakdown Rows
            languages_detail = repo.get("languages_detail", {})
            total_bytes = sum(languages_detail.values()) if languages_detail else 0

            for lang_name, byte_count in languages_detail.items():
                percentage = round((byte_count / total_bytes) * 100, 2) if total_bytes > 0 else 0.0
                langs_list.append({
                    "repo_id": repo_id,
                    "language": lang_name,
                    "bytes": byte_count,
                    "percentage": percentage,
                    "fetched_date": self.today,
                })

            # 4. Topic Tags Rows
            topics = repo.get("topics", [])
            for topic in set(topics):  # Deduplicate topics
                if topic:
                    topics_list.append({
                        "repo_id": repo_id,
                        "topic": str(topic).lower().strip(),
                        "fetched_date": self.today,
                    })

        # Convert lists to Pandas DataFrames
        df_repos = pd.DataFrame(repos_list)
        df_metrics = pd.DataFrame(metrics_list)
        df_langs = pd.DataFrame(langs_list)
        df_topics = pd.DataFrame(topics_list)

        print("[SUCCESS] Transformation Phase Completed:")
        print(f"  - Repositories DataFrame:      {len(df_repos)} rows")
        print(f"  - Repository Metrics DataFrame: {len(df_metrics)} rows")
        print(f"  - Language Breakdown DataFrame:{len(df_langs)} rows")
        print(f"  - Repository Topics DataFrame: {len(df_topics)} rows")

        return {
            "repositories": df_repos,
            "metrics": df_metrics,
            "languages": df_langs,
            "topics": df_topics,
        }


if __name__ == "__main__":
    from src.extractor import GitHubExtractor

    print("==========================================")
    print("      STEP 4 TRANSFORMER TEST            ")
    print("==========================================")

    # 1. Extract sample raw data
    extractor = GitHubExtractor()
    raw_data = extractor.extract_all(target_languages=["Python"], max_per_lang=2)

    # 2. Transform raw data
    transformer = GitHubTransformer()
    transformed_dfs = transformer.transform_all(raw_data)

    print("\n--- PREVIEW OF TRANSFORMED DATAFRAMES ---")
    print("\n[Master Repositories Table Preview]:")
    print(transformed_dfs["repositories"][["repo_id", "full_name", "primary_language", "fetched_date"]].to_string(index=False))

    print("\n[Time-Series Metrics Table Preview]:")
    print(transformed_dfs["metrics"].to_string(index=False))

    print("\n[Language Stats Table Preview (First 5 Rows)]:")
    print(transformed_dfs["languages"].head(5).to_string(index=False))

    print("\nSUCCESS: Step 4 Transformer working cleanly!")
