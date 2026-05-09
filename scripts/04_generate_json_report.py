import sqlite3
import json
from pathlib import Path

DB_PATH = Path("database/patents.db")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get total patents
cursor.execute("SELECT COUNT(*) FROM patents")
total_patents = cursor.fetchone()[0]

# Get top 5 inventors
cursor.execute("""
    SELECT i.name, COUNT(DISTINCT r.patent_id) as patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name
    ORDER BY patent_count DESC
    LIMIT 5
""")
top_inventors = [{"name": row[0], "patents": row[1]} for row in cursor.fetchall()]

# Get top 5 companies
cursor.execute("""
    SELECT c.name, COUNT(DISTINCT r.patent_id) as patent_count
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id, c.name
    ORDER BY patent_count DESC
    LIMIT 5
""")
top_companies = [{"name": row[0], "patents": row[1]} for row in cursor.fetchall()]

# Get top 5 countries
cursor.execute("""
    SELECT 
        CASE 
            WHEN i.country IS NULL OR i.country = '' THEN 'Unknown'
            ELSE i.country 
        END as country,
        COUNT(DISTINCT r.patent_id) as patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY country
    ORDER BY patent_count DESC
    LIMIT 5
""")
total_patents_with_country = sum(row[1] for row in cursor.fetchall())
cursor.execute("""
    SELECT 
        CASE 
            WHEN i.country IS NULL OR i.country = '' THEN 'Unknown'
            ELSE i.country 
        END as country,
        COUNT(DISTINCT r.patent_id) as patent_count
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY country
    ORDER BY patent_count DESC
    LIMIT 5
""")
top_countries = []
for row in cursor.fetchall():
    share = row[1] / total_patents_with_country if total_patents_with_country > 0 else 0
    top_countries.append({"country": row[0], "share": round(share, 3)})

# Create JSON report
report = {
    "total_patents": total_patents,
    "top_inventors": top_inventors,
    "top_companies": top_companies,
    "top_countries": top_countries
}

# Save JSON
json_path = REPORTS_DIR / "report.json"
with open(json_path, 'w') as f:
    json.dump(report, f, indent=2)

print(f"✅ JSON report saved to {json_path}")

# Also print to console
print("\n" + "=" * 50)
print("JSON REPORT SUMMARY")
print("=" * 50)
print(json.dumps(report, indent=2))

conn.close()