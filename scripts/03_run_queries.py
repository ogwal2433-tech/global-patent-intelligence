import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("database/patents.db")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

print("=" * 60)
print("PATENT ANALYSIS REPORT")
print("=" * 60)

# Q1: Top Inventors
print("\n📊 Q1: TOP INVENTORS")
q1 = """
SELECT i.name, COUNT(DISTINCT r.patent_id) as patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 10
"""
top_inventors = pd.read_sql(q1, conn)
print(top_inventors.to_string(index=False))
top_inventors.to_csv(REPORTS_DIR / "top_inventors.csv", index=False)

# Q2: Top Companies
print("\n📊 Q2: TOP COMPANIES")
q2 = """
SELECT c.name, COUNT(DISTINCT r.patent_id) as patent_count
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
GROUP BY c.company_id, c.name
ORDER BY patent_count DESC
LIMIT 10
"""
top_companies = pd.read_sql(q2, conn)
print(top_companies.to_string(index=False))
top_companies.to_csv(REPORTS_DIR / "top_companies.csv", index=False)

# Q3: Top Countries
print("\n📊 Q3: TOP COUNTRIES")
q3 = """
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
LIMIT 10
"""
top_countries = pd.read_sql(q3, conn)
print(top_countries.to_string(index=False))
top_countries.to_csv(REPORTS_DIR / "country_trends.csv", index=False)

# Q4: Trends Over Time
print("\n📊 Q4: PATENTS PER YEAR")
q4 = """
SELECT year, COUNT(*) as patent_count
FROM patents
WHERE year IS NOT NULL AND year > 0
GROUP BY year
ORDER BY year DESC
LIMIT 20
"""
yearly_trends = pd.read_sql(q4, conn)
print(yearly_trends.to_string(index=False))

# Q5: JOIN Query (combine all tables)
print("\n📊 Q5: COMBINED PATENT DATA (Sample 20 rows)")
q5 = """
SELECT p.patent_id, p.title, i.name as inventor_name, c.name as company_name, p.year
FROM patents p
LEFT JOIN relationships r ON p.patent_id = r.patent_id
LEFT JOIN inventors i ON r.inventor_id = i.inventor_id
LEFT JOIN companies c ON r.company_id = c.company_id
WHERE p.title IS NOT NULL
LIMIT 20
"""
combined = pd.read_sql(q5, conn)
print(combined.to_string(index=False))

# Q6: CTE Query (WITH statement)
print("\n📊 Q6: CTE QUERY - Top inventors per year")
q6 = """
WITH yearly_inventor_counts AS (
    SELECT p.year, i.inventor_id, i.name, COUNT(*) as patent_count
    FROM patents p
    JOIN relationships r ON p.patent_id = r.patent_id
    JOIN inventors i ON r.inventor_id = i.inventor_id
    WHERE p.year IS NOT NULL AND p.year > 2000
    GROUP BY p.year, i.inventor_id, i.name
),
ranked_inventors AS (
    SELECT year, name, patent_count,
           ROW_NUMBER() OVER (PARTITION BY year ORDER BY patent_count DESC) as rank
    FROM yearly_inventor_counts
)
SELECT year, name, patent_count
FROM ranked_inventors
WHERE rank <= 3
ORDER BY year DESC, rank
LIMIT 30
"""
cte_results = pd.read_sql(q6, conn)
print(cte_results.to_string(index=False))

# Q7: Ranking Query (Window functions)
print("\n📊 Q7: RANKING QUERY - Top 20 inventors with ranking")
q7 = """
SELECT i.name, COUNT(DISTINCT r.patent_id) as patent_count,
       RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) as rank,
       DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) as dense_rank
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 20
"""
ranking = pd.read_sql(q7, conn)
print(ranking.to_string(index=False))

conn.close()

print("\n" + "=" * 60)
print("✅ Reports saved to 'reports/' directory")
print("   - top_inventors.csv")
print("   - top_companies.csv")
print("   - country_trends.csv")
print("=" * 60)