import os
import sys
import pandas as pd

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.database import db_manager


class AnalyticsEngine:
    """SQL Analytics Engine for querying insights from GitHub Data Warehouse."""

    def __init__(self, db=None):
        self.db = db or db_manager

    def run_query(self, query_sql: str) -> pd.DataFrame:
        """Executes a SQL query and returns results as a Pandas DataFrame."""
        session = self.db.get_session()
        try:
            conn = session.connection()
            df = pd.read_sql_query(query_sql, conn)
            return df
        finally:
            session.close()

    def get_top_starred_repositories(self, limit: int = 10) -> pd.DataFrame:
        """Query 1: Top Most Starred Repositories Across All Languages."""
        query = f"""
            SELECT 
                r.repo_name,
                r.owner,
                r.primary_language,
                rm.stars_count,
                rm.forks_count,
                rm.open_issues
            FROM repositories r
            JOIN repository_metrics rm ON r.repo_id = rm.repo_id
            ORDER BY rm.stars_count DESC
            LIMIT {limit};
        """
        return self.run_query(query)

    def get_language_popularity_summary(self) -> pd.DataFrame:
        """Query 2: Language Ecosystem Summary & Average Stars."""
        query = """
            SELECT 
                r.primary_language,
                COUNT(DISTINCT r.repo_id) AS total_repositories,
                ROUND(AVG(rm.stars_count), 0) AS avg_stars,
                SUM(rm.stars_count) AS total_stars,
                ROUND(AVG(rm.forks_count), 0) AS avg_forks
            FROM repositories r
            JOIN repository_metrics rm ON r.repo_id = rm.repo_id
            GROUP BY r.primary_language
            ORDER BY total_stars DESC;
        """
        return self.run_query(query)

    def get_top_trending_topics(self, limit: int = 15) -> pd.DataFrame:
        """Query 3: Most Frequent Repository Topics / Categories."""
        query = f"""
            SELECT 
                rt.topic,
                COUNT(DISTINCT rt.repo_id) AS repo_count,
                ROUND(AVG(rm.stars_count), 0) AS avg_stars
            FROM repository_topics rt
            JOIN repository_metrics rm ON rt.repo_id = rm.repo_id
            GROUP BY rt.topic
            ORDER BY repo_count DESC, avg_stars DESC
            LIMIT {limit};
        """
        return self.run_query(query)

    def get_community_engagement_ranking(self, limit: int = 10) -> pd.DataFrame:
        """Query 4: Highest Community Engagement (Fork-to-Star Ratio)."""
        query = f"""
            SELECT 
                r.full_name,
                r.primary_language,
                rm.stars_count,
                rm.forks_count,
                ROUND((CAST(rm.forks_count AS FLOAT) / rm.stars_count) * 100, 2) AS fork_ratio_pct
            FROM repositories r
            JOIN repository_metrics rm ON r.repo_id = rm.repo_id
            WHERE rm.stars_count > 1000
            ORDER BY fork_ratio_pct DESC
            LIMIT {limit};
        """
        return self.run_query(query)


if __name__ == "__main__":
    print("==================================================")
    print("        STEP 7 SQL ANALYTICS ENGINE TEST          ")
    print("==================================================")
    
    analytics = AnalyticsEngine()

    print("\n--- INSIGHT 1: TOP 5 MOST STARRED REPOSITORIES ---")
    print(analytics.get_top_starred_repositories(5).to_string(index=False))

    print("\n--- INSIGHT 2: LANGUAGE ECOSYSTEM SUMMARY ---")
    print(analytics.get_language_popularity_summary().to_string(index=False))

    print("\n--- INSIGHT 3: TOP 10 TRENDING TOPICS ---")
    print(analytics.get_top_trending_topics(10).to_string(index=False))

    print("\n--- INSIGHT 4: HIGHEST FORK-TO-STAR RATIO (COMMUNITY ENGAGEMENT) ---")
    print(analytics.get_community_engagement_ranking(5).to_string(index=False))

    print("\nSUCCESS: Step 7 SQL Analytics executed cleanly!")
