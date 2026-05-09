import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("database/patents.db")
RAW_DIR = Path("data")

print("🌍 Adding country data to database...")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Load location data with correct column name
print("  Loading location data...")
locations = pd.read_csv(
    RAW_DIR / "g_location_disambiguated.tsv", 
    sep='\t',
    usecols=['location_id', 'disambig_country']
)
locations = locations.rename(columns={'disambig_country': 'country'})
locations = locations.drop_duplicates(subset=['location_id'])
print(f"    Loaded {len(locations):,} unique locations")

# Load inventors with location data
print("  Loading inventors with location data...")
inventors_with_loc = pd.read_csv(
    RAW_DIR / "g_inventor_disambiguated.tsv",
    sep='\t',
    usecols=['inventor_id', 'disambig_inventor_name_first', 
             'disambig_inventor_name_last', 'location_id']
)

# Create full name
inventors_with_loc['name'] = (
    inventors_with_loc['disambig_inventor_name_first'].fillna('') + ' ' +
    inventors_with_loc['disambig_inventor_name_last'].fillna('')
).str.strip()

# Merge with locations to get country
print("  Merging with location data...")
inventors_with_loc = inventors_with_loc.merge(
    locations[['location_id', 'country']],
    on='location_id',
    how='left'
)

# Deduplicate by inventor_id (keep first occurrence)
print("  Deduplicating inventors...")
inventors_with_loc = inventors_with_loc.drop_duplicates(subset=['inventor_id'], keep='first')

# Prepare final inventors table
final_inventors = inventors_with_loc[['inventor_id', 'name', 'country']].copy()
print(f"    Total unique inventors: {len(final_inventors):,}")

# Show sample of what we got
print("\n  Sample inventors with countries:")
sample = final_inventors[final_inventors['country'].notna()].head(10)
for _, row in sample.iterrows():
    print(f"    {row['inventor_id'][:20]}... {row['name'][:30]} -> {row['country']}")

# Method 2: Update the existing table instead of replacing it
print("\n  Updating inventors table with country data...")

# First, add country column if it doesn't exist
try:
    cursor.execute("ALTER TABLE inventors ADD COLUMN country_temp TEXT")
except sqlite3.OperationalError:
    cursor.execute("ALTER TABLE inventors ADD COLUMN country_temp TEXT")

# Create a temporary table with updated data
cursor.execute("BEGIN TRANSACTION")

# Create a mapping of inventor_id to country
print("  Creating country lookup...")
country_lookup = dict(zip(final_inventors['inventor_id'], final_inventors['country']))

# Update each inventor's country
print("  Updating countries (this may take a few minutes)...")
cursor.execute("SELECT inventor_id FROM inventors")
inventor_ids = cursor.fetchall()

updated = 0
for (inventor_id,) in inventor_ids:
    country = country_lookup.get(inventor_id)
    if country:
        cursor.execute("UPDATE inventors SET country_temp = ? WHERE inventor_id = ?", (country, inventor_id))
        updated += 1
    if updated % 100000 == 0:
        print(f"    Updated {updated:,} inventors...", end='\r')

# Copy temp column to country column
print(f"\n    Updated {updated:,} inventors with country data")
cursor.execute("UPDATE inventors SET country = country_temp")
cursor.execute("ALTER TABLE inventors DROP COLUMN country_temp")

conn.commit()

# Show results
print("\n  📊 Top countries by inventor count:")
cursor.execute("""
    SELECT 
        CASE 
            WHEN country IS NULL OR country = '' THEN 'Unknown'
            ELSE country 
        END as country,
        COUNT(*) as inventor_count
    FROM inventors
    GROUP BY country
    ORDER BY inventor_count DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"    {row[0]}: {row[1]:,} inventors")

# Patents by inventor country (for Q3)
print("\n  📊 Patents by inventor country (for Q3):")
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
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"    {row[0]}: {row[1]:,} patents")

conn.commit()
conn.close()

print("\n✅ Country data added successfully!")
print("   Run 'python scripts/03_run_queries.py' again to see updated Q3 results")