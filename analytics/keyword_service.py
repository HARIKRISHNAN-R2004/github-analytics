import os
import sys
from typing import Dict, Any, List

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.extractor import GitHubExtractor
from src.transformer import GitHubTransformer
from src.loader import GitHubLoader
from src.database import db_manager
from analytics.export_dashboard_data import export_dashboard_json


class KeywordSearchService:
    """Service for running live keyword-based GitHub search, ETL, and result aggregation."""

    def __init__(self):
        self.extractor = GitHubExtractor()
        self.transformer = GitHubTransformer()
        self.loader = GitHubLoader(db=db_manager)

    def execute_keyword_etl(self, keyword: str, max_results: int = 15) -> Dict[str, Any]:
        """
        Executes end-to-end Keyword Search ETL:
        1. Extract matching repositories live from GitHub API for user keyword.
        2. Transform raw JSON into clean Pandas DataFrames.
        3. Load into SQLite database.
        4. Return clean structured JSON results for display on the web page.
        """
        keyword = keyword.strip()
        if not keyword:
            return {"error": "Keyword cannot be empty", "repositories": []}

        print(f"\n[KEYWORD ETL] Processing live search for keyword: '{keyword}'...")

        # 1. Extract
        raw_repos = self.extractor.search_by_keyword(keyword=keyword, max_repos=max_results)
        if not raw_repos:
            return {
                "keyword": keyword,
                "total_found": 0,
                "repositories": [],
                "message": f"No repositories found matching '{keyword}'."
            }

        # 2. Transform
        dfs = self.transformer.transform_all(raw_repos)

        # 3. Load into Database Warehouse
        self.loader.load_all(dfs)

        # 4. Refresh Dashboard Data
        export_dashboard_json()

        # Format output list for Web Page Display
        formatted_results = []
        df_repos = dfs["repositories"]
        df_metrics = dfs["metrics"]
        df_langs = dfs["languages"]

        for _, repo_row in df_repos.iterrows():
            repo_id = repo_row["repo_id"]
            metric_row = df_metrics[df_metrics["repo_id"] == repo_id].iloc[0] if not df_metrics[df_metrics["repo_id"] == repo_id].empty else {}
            
            # Languages list for this repo
            repo_langs = df_langs[df_langs["repo_id"] == repo_id].to_dict(orient="records") if not df_langs.empty else []

            formatted_results.append({
                "repo_id": int(repo_id),
                "owner": repo_row["owner"],
                "repo_name": repo_row["repo_name"],
                "full_name": repo_row["full_name"],
                "url": repo_row["url"],
                "description": repo_row["description"],
                "primary_language": repo_row["primary_language"],
                "stars_count": int(metric_row.get("stars_count", 0)),
                "forks_count": int(metric_row.get("forks_count", 0)),
                "open_issues": int(metric_row.get("open_issues", 0)),
                "language_breakdown": repo_langs,
            })

        return {
            "keyword": keyword,
            "total_found": len(formatted_results),
            "repositories": formatted_results,
        }


if __name__ == "__main__":
    service = KeywordSearchService()
    test_keyword = "cybersecurity"
    print(f"Testing Keyword Search Service for: '{test_keyword}'...")
    res = service.execute_keyword_etl(test_keyword, max_results=3)
    print(f"\nFound {res['total_found']} repositories:")
    for r in res.get("repositories", []):
        print(f" - {r['full_name']} (Stars: {r['stars_count']:,}) | {r['primary_language']}")
