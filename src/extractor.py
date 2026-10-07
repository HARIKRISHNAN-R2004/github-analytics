import os
import sys
import requests
import time
from typing import List, Dict, Any

# Ensure project root is in sys.path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config


class GitHubExtractor:
    """Extractor component for fetching raw repository data from GitHub REST API v3."""

    def __init__(self):
        self.base_url = config.GITHUB_API_BASE_URL
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Analytics-ETL-Pipeline",
        }
        if config.GITHUB_TOKEN:
            self.headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"

    def safe_get(self, url: str, params: dict = None, retries: int = 3) -> requests.Response:
        """Helper method to make robust HTTP requests with retry logic."""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                return response
            except requests.exceptions.RequestException as e:
                print(f"  [RETRY {attempt+1}/{retries}] Network error: {e}. Retrying in 1s...")
                time.sleep(1)
        return None

    def fetch_trending_repositories(
        self, language: str, min_stars: int = 100, max_repos: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch top trending repositories for a given programming language."""
        search_url = f"{self.base_url}/search/repositories"
        query = f"language:{language} stars:>{min_stars}"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(max_repos, 100),
        }

        print(f"  [API] Fetching top {max_repos} {language} repositories...")
        response = self.safe_get(search_url, params=params)

        if not response or response.status_code != 200:
            status = response.status_code if response else "No Response"
            print(f"  [ERROR] GitHub API returned status {status}")
            return []

        data = response.json()
        items = data.get("items", [])
        print(f"  [OK] Successfully fetched {len(items)} repositories for {language}.")
        return items

    def search_by_keyword(
        self, keyword: str, min_stars: int = 0, max_repos: int = 20
    ) -> List[Dict[str, Any]]:
        """Dynamically search repositories based on any user-provided keyword."""
        search_url = f"{self.base_url}/search/repositories"
        query = f"{keyword} stars:>{min_stars}" if min_stars > 0 else keyword
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(max_repos, 100),
        }

        print(f"  [API Search] Searching GitHub for keyword '{keyword}' (max {max_repos} repos)...")
        response = self.safe_get(search_url, params=params)

        if not response or response.status_code != 200:
            status = response.status_code if response else "No Response"
            print(f"  [ERROR] GitHub Search API error {status}")
            return []

        items = response.json().get("items", [])
        
        # Enrich each repo with detailed language breakdown
        for repo in items:
            owner = repo.get("owner", {}).get("login", "")
            repo_name = repo.get("name", "")
            languages_breakdown = self.fetch_repository_languages(owner, repo_name)
            repo["languages_detail"] = languages_breakdown
            time.sleep(0.1)  # Polite API delay

        print(f"  [OK] Found {len(items)} repositories matching keyword '{keyword}'.")
        return items

    def fetch_repository_languages(self, owner: str, repo_name: str) -> Dict[str, int]:
        """Fetch language byte breakdown for a specific repository."""
        lang_url = f"{self.base_url}/repos/{owner}/{repo_name}/languages"
        response = self.safe_get(lang_url)
        if response and response.status_code == 200:
            return response.json()
        return {}

    def extract_all(self, target_languages: List[str] = None, max_per_lang: int = 5) -> List[Dict[str, Any]]:
        """Main extraction process for all target languages configured."""
        if target_languages is None:
            target_languages = config.TARGET_LANGUAGES

        all_extracted_repos = []
        print(f"\n[START] Starting Extraction Phase for languages: {', '.join(target_languages)}...")

        for lang in target_languages:
            repos = self.fetch_trending_repositories(
                language=lang,
                min_stars=config.MIN_STARS,
                max_repos=max_per_lang,
            )

            for repo in repos:
                owner = repo.get("owner", {}).get("login", "")
                repo_name = repo.get("name", "")
                languages_breakdown = self.fetch_repository_languages(owner, repo_name)
                repo["languages_detail"] = languages_breakdown
                all_extracted_repos.append(repo)
                time.sleep(0.2)

        print(f"[SUCCESS] Extraction Phase Completed: {len(all_extracted_repos)} total repos collected.")
        return all_extracted_repos


if __name__ == "__main__":
    extractor = GitHubExtractor()
    results = extractor.search_by_keyword("agent", min_stars=500, max_repos=3)
    for r in results:
        print(f"Repo: {r.get('full_name')} | Stars: {r.get('stargazers_count'):,} | Lang: {r.get('language')}")
