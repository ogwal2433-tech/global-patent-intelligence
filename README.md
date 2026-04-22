# Global Patent Intelligence Pipeline

**Makerere University — Data Engineering Assignment**
**Author:** Ogwal Richard | **Student No:** 2300716574

---

## Overview

A complete end-to-end data engineering pipeline that collects, cleans, stores, and analyzes real-world patent data from the USPTO PatentsView database (1976–2025).

| Metric | Value |
|---|---|
| Total Patents | 9,454,161 |
| Total Inventors | 4,294,032 |
| Total Companies | 572,495 |
| Total Relationships | 25,292,037 |
| Raw Data Size | ~10.7 GB |
| Processed Data | ~8 GB |

**Data Source:** [USPTO PatentsView](https://patentsview.org/) — Granted Patent Data, 1976–2025

---

## Requirements Met

| Requirement | Status | Location |
|---|---|---|
| Python scripts | ✅ | `scripts/` |
| SQL schema | ✅ | `sql/schema.sql` |
| Clean CSV files | ✅ | `data/clean/` |
| Console report | ✅ | Terminal output |
| CSV reports (3 files) | ✅ | `reports/` |
| JSON report | ✅ | `reports/report.json` |
| Streamlit dashboard (extra) | ✅ | `scripts/06_dashboard.py` |

---

## Project Structure

```
global-patent-intelligence/
│
├── data/
│   └── clean/
│       ├── clean_patents.csv          # 9,454,161 rows
│       ├── clean_inventors.csv        # 4,294,032 rows
│       ├── clean_companies.csv        # 572,495 rows
│       └── clean_relationships.csv    # 25,292,037 rows
│
├── database/
│   └── patents.db                     # SQLite database (~6 GB)
│
├── reports/
│   ├── top_inventors.csv
│   ├── top_companies.csv
│   ├── country_trends.csv
│   └── report.json
│
├── scripts/
│   ├── 01_clean_with_cleaning_steps.py
│   ├── 02_load_to_sqlite.py
│   ├── 03_run_queries.py
│   ├── 04_generate_json_report.py
│   ├── 05_add_countries.py
│   └── 06_dashboard.py
│
├── sql/
│   └── schema.sql
│
├── requirements.txt
└── README.md
```

---

## Database Schema

### Tables

| Table | Key Columns | Rows |
|---|---|---|
| `patents` | patent_id, title, abstract, filing_date, year | 9,454,161 |
| `inventors` | inventor_id, name, country | 4,294,032 |
| `companies` | company_id, name | 572,495 |
| `relationships` | patent_id, inventor_id, company_id | 25,292,037 |

### Entity Relationship Diagram

```
patents ──┐
          ├── relationships ── inventors
companies ┘
```

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- 8 GB+ RAM (16 GB recommended)
- 20 GB free disk space

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/global-patent-intelligence.git
cd global-patent-intelligence
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download Raw Data

Download the following files from [PatentsView](https://patentsview.org/download/data-download-tables) and place them in `data/raw/`:

| File | Size |
|---|---|
| `g_patent.tsv` | 1.1 GB |
| `g_patent_abstract.tsv` | 6.2 GB |
| `g_inventor_disambiguated.tsv` | 2.3 GB |
| `g_assignee_disambiguated.tsv` | 1.1 GB |
| `g_location_disambiguated.tsv` | 2.7 MB |

---

## Running the Pipeline

Run each step in order:

### Step 1 — Clean the Data

```bash
python scripts/01_clean_with_cleaning_steps.py
```

Operations performed:
- Handle missing values (NULLs, empty strings)
- Remove duplicate records
- Extract year from filing date
- Merge abstracts with patents
- Standardize column names
- Create normalized relationships table

### Step 2 — Load into SQLite

```bash
python scripts/02_load_to_sqlite.py
```

### Step 3 — Enrich with Country Data

```bash
python scripts/05_add_countries.py
```

### Step 4 — Run Analysis Queries

```bash
python scripts/03_run_queries.py
```

### Step 5 — Generate JSON Report

```bash
python scripts/04_generate_json_report.py
```

### Step 6 — Launch Dashboard (Optional)

```bash
streamlit run scripts/06_dashboard.py
```

### Quick Start (One-Liner)

```bash
pip install -r requirements.txt && \
python scripts/01_clean_with_cleaning_steps.py && \
python scripts/02_load_to_sqlite.py && \
python scripts/05_add_countries.py && \
python scripts/03_run_queries.py && \
python scripts/04_generate_json_report.py
```

---

## The 7 SQL Queries

| # | Query | Description |
|---|---|---|
| Q1 | Top Inventors | Who has the most patents? |
| Q2 | Top Companies | Which companies own the most patents? |
| Q3 | Top Countries | Which countries produce the most patents? |
| Q4 | Trends Over Time | How many patents are filed per year? |
| Q5 | JOIN Query | Combine patents with inventors and companies |
| Q6 | CTE Query | Complex analysis using `WITH` statement |
| Q7 | Ranking Query | Rank inventors using `RANK` and `DENSE_RANK` window functions |

---

## Results Summary

### Q1 — Top 5 Inventors

| Rank | Inventor | Patents |
|---|---|---|
| 1 | Shunpei Yamazaki | 6,787 |
| 2 | Kia Silverbrook | 4,778 |
| 3 | Tao Luo | 4,490 |
| 4 | Jonathan P. Ive | 2,947 |
| 5 | Junyi Li | 2,881 |

### Q2 — Top 5 Companies

| Rank | Company | Patents |
|---|---|---|
| 1 | Samsung Display Co., Ltd. | 174,536 |
| 2 | International Business Machines Corporation | 164,083 |
| 3 | Canon Kabushiki Kaisha | 91,331 |
| 4 | Sony Group Corporation | 62,911 |
| 5 | Fujitsu Limited | 56,343 |

### Q3 — Top 5 Countries

| Rank | Country | Patents | Share |
|---|---|---|---|
| 1 | United States (US) | 5,152,235 | 61.9% |
| 2 | Japan (JP) | 1,596,388 | 19.2% |
| 3 | Germany (DE) | 632,808 | 7.6% |
| 4 | China (CN) | 503,914 | 6.1% |
| 5 | South Korea (KR) | 441,206 | 5.3% |

### Q4 — Patent Trends

- **Peak Year:** 2019 — 392,618 patents
- **Recent Activity:** 2025 — 378,741 patents
- **Growth Period:** Consistent growth from 2006 to 2019

### Q6 — CTE: Top Inventor Per Year (Sample)

| Year | Top Inventor | Patents |
|---|---|---|
| 2025 | Tao Luo | 763 |
| 2024 | Tao Luo | 860 |
| 2023 | Tao Luo | 1,057 |

### Q7 — Ranking Query Results

| Rank | Inventor | Patents |
|---|---|---|
| 1 | Shunpei Yamazaki | 6,787 |
| 2 | Kia Silverbrook | 4,778 |
| 3 | Tao Luo | 4,490 |

---

## Output Files

### CSV Reports (`reports/`)

- `top_inventors.csv` — Top 10 inventors with patent counts
- `top_companies.csv` — Top 10 companies with patent counts
- `country_trends.csv` — Top 10 countries with patent counts

### JSON Report (`reports/report.json`)

```json
{
  "total_patents": 9454161,
  "top_inventors": [...],
  "top_companies": [...],
  "top_countries": [...]
}
```

---

## Dashboard

An interactive Streamlit dashboard is available for visual exploration:

```bash
streamlit run scripts/06_dashboard.py
```

Features include key metrics (total patents, inventors, companies), patent trends over time (line chart), country distribution (pie chart), top inventors and companies (bar charts), a year-over-year comparison tool, and a recent activity table.

---

## Data Cleaning Summary

| Operation | Method | Purpose |
|---|---|---|
| Missing values | `fillna("")` | Handle NULLs in name fields |
| Duplicate removal | `drop_duplicates()` | Remove duplicate inventors/companies |
| Date parsing | `pd.to_datetime()` | Extract year from filing_date |
| Data merging | `merge()` | Join abstracts with patents |
| Column renaming | `rename()` | Standardize column names |
| Data filtering | `dropna()` | Remove invalid records |
| Normalization | Separate relationships table | Clean, structured schema |

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| pandas | Data cleaning and transformation |
| SQLite | Database storage and queries |
| SQL | Analytical queries (CTEs, window functions) |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |

---

## Notes

- **Memory:** Full dataset requires 8–16 GB RAM
- **Processing Time:** Complete pipeline takes 30–45 minutes on an 8 GB machine
- **Country Coverage:** approximately 98.5% of patents have country data (140,946 unknown)
- **Database Size:** `patents.db` is approximately 6 GB

---

## Reproducibility

This pipeline is fully reproducible. Clone the repo, download the raw data, and run the scripts in order (01 → 02 → 05 → 03 → 04). The same results are guaranteed on every run.

---

## Author

**Ogwal Richard**
Student Number: `2300716574`
Makerere University — School of Computing and Information  Technology
Data Engineering Assignment, cloud computing
