import os
import sys
import json
from pathlib import Path

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from analytics.sql_queries import AnalyticsEngine

def export_dashboard_json():
    analytics = AnalyticsEngine()
    
    top_repos = analytics.get_top_starred_repositories(10).to_dict(orient="records")
    lang_summary = analytics.get_language_popularity_summary().to_dict(orient="records")
    top_topics = analytics.get_top_trending_topics(10).to_dict(orient="records")
    engagement = analytics.get_community_engagement_ranking(10).to_dict(orient="records")

    data = {
        "generated_at": "2026-10-06",
        "top_repositories": top_repos,
        "language_summary": lang_summary,
        "top_topics": top_topics,
        "community_engagement": engagement,
    }

    out_dir = Path(__file__).parent.parent / "dashboard"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "dashboard_data.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[EXPORT] Dashboard dataset exported to: {out_file.resolve()}")

if __name__ == "__main__":
    export_dashboard_json()
