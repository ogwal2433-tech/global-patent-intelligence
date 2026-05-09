import sqlite3
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
CLEAN_DIR = Path("data/clean")
SQL_DIR = Path("sql")
DB_PATH = Path("database/patents.db")

# Create directories
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

print("🔗 Loading data into SQLite database (chunked for memory efficiency)...")

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Read and execute schema.sql
print("  Creating schema...")
with open(SQL_DIR / "schema.sql", 'r') as f:
    schema_sql = f.read()
conn.executescript(schema_sql)

# Load patents in chunks
print("  Loading patents...")
chunk_size = 100000
for chunk in pd.read_csv(CLEAN_DIR / "clean_patents.csv", chunksize=chunk_size, low_memory=False):
    chunk.to_sql('patents', conn, if_exists='append', index=False)
print("    ✅ Patents loaded")

# Load inventors in chunks
print("  Loading inventors...")
for chunk in pd.read_csv(CLEAN_DIR / "clean_inventors.csv", chunksize=chunk_size, low_memory=False):
    chunk.to_sql('inventors', conn, if_exists='append', index=False)
print("    ✅ Inventors loaded")

# Load companies in chunks
print("  Loading companies...")
for chunk in pd.read_csv(CLEAN_DIR / "clean_companies.csv", chunksize=chunk_size, low_memory=False):
    chunk.to_sql('companies', conn, if_exists='append', index=False)
print("    ✅ Companies loaded")

# Load relationships in chunks (this was the problem)
print("  Loading relationships...")
for chunk in pd.read_csv(CLEAN_DIR / "clean_relationships.csv", chunksize=chunk_size, low_memory=False):
    chunk.to_sql('relationships', conn, if_exists='append', index=False)
print("    ✅ Relationships loaded")

# Create indexes for faster queries
print("  Creating indexes...")
conn.execute("CREATE INDEX IF NOT EXISTS idx_patents_year ON patents(year)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_patents_id ON patents(patent_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_inventors_id ON inventors(inventor_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_companies_id ON companies(company_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_patent ON relationships(patent_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_inventor ON relationships(inventor_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_company ON relationships(company_id)")

conn.commit()

# Verify counts
print("\n✅ Database created successfully!")
print(f"   Location: {DB_PATH}")

cursor = conn.cursor()
tables = ['patents', 'inventors', 'companies', 'relationships']
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   {table}: {count:,} rows")

conn.close()