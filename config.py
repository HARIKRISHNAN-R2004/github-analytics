import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")


class Config:
    """Central configuration for GitHub Analytics ETL Pipeline."""

    # GitHub API Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
    GITHUB_API_BASE_URL = "https://api.github.com"

    # Extraction Settings
    MIN_STARS = int(os.getenv("MIN_STARS", 100))
    MAX_REPOS_PER_LANG = int(os.getenv("MAX_REPOS_PER_LANG", 20))
    TARGET_LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "Java",
    "C++",
    "C#",
    "PHP"
]
    # Database Configuration (Defaults to SQLite for local development)
    DATABASE_URL = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'github_analytics.db'}"
    )

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "pipeline.log"


# Instantiated settings object
config = Config()

if __name__ == "__main__":
    print("==========================================")
    print("      STEP 1 CONFIGURATION TEST          ")
    print("==========================================")
    print(f"Project Base Path: {BASE_DIR}")
    print(f"Database URL:      {config.DATABASE_URL}")
    print(f"Target Languages:  {', '.join(config.TARGET_LANGUAGES)}")
    print(f"Min Stars Filter:  {config.MIN_STARS}")
    print(f"GitHub Token Set:  {'YES' if config.GITHUB_TOKEN else 'NO (Using Public Rate Limits)'}")
    print("==========================================")
    print("SUCCESS: Step 1 configuration loaded cleanly!")
