# 🚀 GitHub Repository Analytics ETL System

An end-to-end **Data Engineering & Business Intelligence Pipeline** built with Python, Pandas, SQLAlchemy, and SQLite. This system extracts live repository metrics from the GitHub REST API v3, cleans and transforms raw data, loads it into a relational database warehouse, and visualizes market trends on an interactive Web Dashboard.

Created by **[HARIKRISHNAN-R2004](https://github.com/HARIKRISHNAN-R2004)**.

---

## 🌟 Key Features

- **Automated ETL Pipeline**: Extracts 100+ repositories across multiple programming language ecosystems (`Python`, `JavaScript`, `TypeScript`, `Go`, `Rust`, `Java`, `C++`, etc.).
- **Live Dynamic Keyword Search**: Perform live GitHub searches on ANY custom keyword (e.g. `cybersecurity`, `machine learning`, `flutter`), run real-time ETL, and visualize repository metrics instantly.
- **Relational Data Warehouse**: Built using a Star Schema pattern (`repositories`, `repository_metrics`, `language_stats`, `repository_topics`) with SQLAlchemy ORM.
- **Data Transformation & Cleaning**: Handles missing data, parses ISO 8601 timestamps, computes language byte percentages, and normalizes tags with Pandas.
- **Interactive Web BI Dashboard**: High-contrast Matte Black & Yellow theme built with Chart.js, featuring language distributions, topic doughnut charts, and community engagement leaderboards.
- **ACID Transaction Safety**: Complete rollback protection on database loading.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                 ETL PIPELINE ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────┘

 TIER 1: DATA SOURCE         TIER 2: EXTRACT LAYER (requests)
 ┌─────────────────┐         ┌───────────────────────────────┐
 │  GitHub API v3  ├────────►│ src/extractor.py              │
 └─────────────────┘         │ - GET /search/repositories    │
                             │ - GET /repos/{owner}/{repo}/  │
                             └──────────────┬────────────────┘
                                            │
                                            ▼
 TIER 4: STORAGE (SQLite)    TIER 3: TRANSFORM LAYER (Pandas)
 ┌─────────────────┐         ┌───────────────────────────────┐
 │ github_         │◄────────┤ src/transformer.py            │
 │ analytics.db    │         │ - Clean & parse ISO timestamps│
 └────────┬────────┘         │ - Calculate % language stats  │
          │                  └───────────────────────────────┘
          ▼
 TIER 5: WEB BI DASHBOARD & REST API
 ┌───────────────────────────────────────────────────────────┐
 │ dashboard/index.html & dashboard/search.html               │
 └───────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Directory Structure

```text
github-analytics/
├── .env                              # Environment variables (GITHUB_TOKEN, DB_URL)
├── .gitignore                        # Git exclusion rules
├── config.py                         # Centralized configuration manager
├── main.py                           # Full pipeline orchestrator & execution entrypoint
├── view_db.py                        # Database Inspector CLI tool
├── README.md                         # Project documentation
├── src/
│   ├── __init__.py
│   ├── extractor.py                  # API Extraction module
│   ├── database.py                   # SQLAlchemy ORM relational models
│   ├── transformer.py                # Pandas data cleaning & transformation
│   └── loader.py                     # Database loading & transaction manager
├── analytics/
│   ├── sql_queries.py                # SQL business intelligence analytics
│   ├── keyword_service.py            # Live Keyword Search ETL service
│   └── export_dashboard_data.py      # JSON dataset exporter for web UI
└── dashboard/
    ├── server.py                     # Python HTTP API & Web Server
    ├── index.html                    # Warehouse Analytics Web Dashboard
    ├── search.html                   # Live Keyword Search Page
    └── dashboard_data.json           # Aggregated dataset
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.9+** installed.

### 2. Installation & Setup
Clone the repository and install required packages:

```bash
git clone https://github.com/HARIKRISHNAN-R2004/github-analytics.git
cd github-analytics
pip install requests pandas sqlalchemy python-dotenv pytest
```

### 3. Run Full ETL Pipeline
Execute the main orchestrator script:

```bash
python main.py
```

### 4. Launch Web Dashboard & REST API
Run the local HTTP server:

```bash
python dashboard/server.py
```

Open your browser and navigate to:
- 📊 **Analytics Dashboard**: `http://localhost:8050/index.html`
- 🔍 **Live Keyword Search Engine**: `http://localhost:8050/search.html`

### 5. Inspect SQLite Database
View database table rows and previews via terminal:

```bash
python view_db.py
```

---

## 👨‍💻 Author

**HARIKRISHNAN R**  
GitHub Profile: [https://github.com/HARIKRISHNAN-R2004](https://github.com/HARIKRISHNAN-R2004)  
Project Category: Data Engineering & Analytics  
License: MIT
