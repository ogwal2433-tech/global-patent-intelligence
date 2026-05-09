import sqlite3
import pandas as pd

conn = sqlite3.connect('database/patents.db')

print("=" * 50)
print("DATABASE PREVIEW")
print("=" * 50)

# Show all tables
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print("\n📁 Tables in database:")
print(tables.to_string(index=False))

# Row counts
print("\n📊 Row counts:")
for table in ['patents', 'inventors', 'companies', 'relationships']:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"   {table}: {count:,}")

# Sample from patents
print("\n📄 Sample patents (first 5):")
df = pd.read_sql("SELECT patent_id, title, year FROM patents LIMIT 5", conn)
print(df.to_string(index=False))

# Sample from inventors
print("\n👨‍🔬 Sample inventors (first 5):")
df = pd.read_sql("SELECT inventor_id, name, country FROM inventors LIMIT 5", conn)
print(df.to_string(index=False))

# Sample from companies
print("\n🏢 Sample companies (first 5):")
df = pd.read_sql("SELECT company_id, name FROM companies LIMIT 5", conn)
print(df.to_string(index=False))

conn.close()
print("\n✅ Done!")