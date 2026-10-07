import os
import sys
import time
import logging
from datetime import datetime

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from config import config
from src.extractor import GitHubExtractor
from src.transformer import GitHubTransformer
from src.loader import GitHubLoader
from src.database import db_manager
from analytics.export_dashboard_data import export_dashboard_json


def setup_logger():
    """Configure logging to file and console."""
    logger = logging.getLogger("ETL_Pipeline")
    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    # File Handler
    file_handler = logging.FileHandler(config.LOG_FILE, mode="a")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def run_etl_pipeline():
    """Main orchestration function executing Extract -> Transform -> Load -> Export Dashboard."""
    logger = setup_logger()

    logger.info("==================================================")
    logger.info("  STARTING GITHUB REPOSITORY ANALYTICS ETL RUN   ")
    logger.info("==================================================")
    start_time = time.time()

    try:
        # Step 1: Initialize Database Schema
        logger.info("[DB] Initializing database tables...")
        db_manager.init_db()

        # Step 2: Extract Phase
        logger.info("[EXTRACT] Fetching trending repositories from GitHub API...")
        extractor = GitHubExtractor()
        raw_data = extractor.extract_all(
            target_languages=config.TARGET_LANGUAGES,
            max_per_lang=config.MAX_REPOS_PER_LANG,
        )

        if not raw_data:
            logger.warning("[EXTRACT] No data extracted! Exiting pipeline.")
            return

        logger.info(f"[EXTRACT] Successfully extracted {len(raw_data)} raw repository records.")

        # Step 3: Transform Phase
        logger.info("[TRANSFORM] Cleaning, validating, and structuring extracted data...")
        transformer = GitHubTransformer()
        transformed_dfs = transformer.transform_all(raw_data)

        # Step 4: Load Phase
        logger.info("[LOAD] Loading transformed DataFrames into database warehouse...")
        loader = GitHubLoader(db=db_manager)
        load_summary = loader.load_all(transformed_dfs)

        # Step 5: Export Dashboard Data
        logger.info("[DASHBOARD] Refreshing web dashboard dataset (dashboard_data.json)...")
        export_dashboard_json()

        elapsed_time = round(time.time() - start_time, 2)
        logger.info("==================================================")
        logger.info("   PIPELINE EXECUTION SUMMARY (SUCCESS)           ")
        logger.info("==================================================")
        logger.info(f"Execution Time:          {elapsed_time} seconds")
        logger.info(f"Target Languages:        {', '.join(config.TARGET_LANGUAGES)}")
        logger.info(f"Master Repos Processed:  {load_summary.get('repositories', 0)}")
        logger.info(f"Time-Series Metrics:     {load_summary.get('metrics', 0)}")
        logger.info(f"Language Stats Rows:     {load_summary.get('languages', 0)}")
        logger.info(f"Topic Tag Rows:          {load_summary.get('topics', 0)}")
        logger.info("==================================================")

    except Exception as e:
        logger.error(f"[PIPELINE FAILURE] Pipeline crashed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_etl_pipeline()
