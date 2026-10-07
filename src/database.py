import os
import sys
from datetime import datetime, date
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Float,
    DateTime,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Ensure project root is in sys.path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config

# SQLAlchemy Base Declarative Class
Base = declarative_base()


class Repository(Base):
    """Master Repository Table (Dimension)"""

    __tablename__ = "repositories"

    repo_id = Column(BigInteger, primary_key=True)
    owner = Column(String(255), nullable=False)
    repo_name = Column(String(255), nullable=False)
    full_name = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    primary_language = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    fetched_date = Column(Date, default=date.today, nullable=False)

    # Relationships
    metrics = relationship("RepositoryMetrics", back_populates="repository", cascade="all, delete-orphan")
    languages = relationship("LanguageStats", back_populates="repository", cascade="all, delete-orphan")
    topics = relationship("RepositoryTopics", back_populates="repository", cascade="all, delete-orphan")


class RepositoryMetrics(Base):
    """Time-Series Snapshot Metrics Table (Fact Table)"""

    __tablename__ = "repository_metrics"

    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(BigInteger, ForeignKey("repositories.repo_id"), nullable=False)
    stars_count = Column(Integer, nullable=False, default=0)
    forks_count = Column(Integer, nullable=False, default=0)
    watchers_count = Column(Integer, nullable=False, default=0)
    open_issues = Column(Integer, nullable=False, default=0)
    fetched_date = Column(Date, default=date.today, nullable=False)

    repository = relationship("Repository", back_populates="metrics")


class LanguageStats(Base):
    """Breakdown of Language Byte Usage per Repository"""

    __tablename__ = "language_stats"

    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(BigInteger, ForeignKey("repositories.repo_id"), nullable=False)
    language = Column(String(100), nullable=False)
    bytes = Column(Integer, nullable=False, default=0)
    percentage = Column(Float, nullable=False, default=0.0)
    fetched_date = Column(Date, default=date.today, nullable=False)

    repository = relationship("Repository", back_populates="languages")


class RepositoryTopics(Base):
    """Topics / Categories Tagged to Repositories"""

    __tablename__ = "repository_topics"

    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(BigInteger, ForeignKey("repositories.repo_id"), nullable=False)
    topic = Column(String(100), nullable=False)
    fetched_date = Column(Date, default=date.today, nullable=False)

    repository = relationship("Repository", back_populates="topics")


class DatabaseManager:
    """Manages database connection and session creation."""

    def __init__(self, db_url: str = None):
        self.db_url = db_url or config.DATABASE_URL
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        """Create all tables defined in Base metadata."""
        print(f"[DB] Initializing database schema at: {self.db_url}")
        Base.metadata.create_all(bind=self.engine)
        print("[DB] All tables created successfully!")

    def get_session(self):
        """Provide a transactional database session."""
        return self.SessionLocal()


# Global database instance
db_manager = DatabaseManager()

if __name__ == "__main__":
    print("==========================================")
    print("      STEP 3 DATABASE ENGINE TEST        ")
    print("==========================================")
    
    db_manager.init_db()
    
    # Inspect created tables using SQLAlchemy Inspector
    from sqlalchemy import inspect
    inspector = inspect(db_manager.engine)
    table_names = inspector.get_table_names()
    
    print("\n--- CREATED TABLES IN DATABASE ---")
    for tbl in table_names:
        cols = [c["name"] for c in inspector.get_columns(tbl)]
        print(f"  Table: {tbl:<20} | Columns: {', '.join(cols)}")
        
    print("\nSUCCESS: Step 3 Database Schema created cleanly!")
