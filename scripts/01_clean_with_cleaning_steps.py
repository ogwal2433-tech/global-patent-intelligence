"""
CLEANING OPERATIONS PERFORMED:
1. Handle missing values (NULLs, empty strings)
2. Remove duplicate records
3. Extract year from date field
4. Merge abstract text with patent records
5. Standardize column names
6. Filter out invalid data (bad dates, empty titles)
7. Create relationships between tables
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data")
CLEAN_DIR = Path("data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("DATA CLEANING PIPELINE")
print("=" * 60)

# =========================================================
# CLEANING STEP 1: Load and clean abstracts
# =========================================================
print("\n📘 CLEANING STEP 1: Processing abstracts")
print("   Operation: Load abstract text for each patent")

abstract_dict = {}
for chunk in pd.read_csv(
    RAW_DIR / "g_patent_abstract.tsv",
    sep="\t",
    usecols=["patent_id", "patent_abstract"],
    chunksize=500000
):
    # Clean: Remove empty abstracts
    chunk = chunk[chunk['patent_abstract'].notna()]
    abstract_dict.update(dict(zip(chunk["patent_id"], chunk["patent_abstract"])))

print(f"   ✅ Loaded {len(abstract_dict):,} abstracts")

# =========================================================
# CLEANING STEP 2: Clean patents
# =========================================================
print("\n📄 CLEANING STEP 2: Cleaning patents table")

patent_output = CLEAN_DIR / "clean_patents.csv"
first_chunk = True
total_patents = 0
removed_no_title = 0
removed_bad_date = 0

for chunk in pd.read_csv(
    RAW_DIR / "g_patent.tsv",
    sep="\t",
    usecols=["patent_id", "patent_title", "patent_date"],
    chunksize=500000
):
    # Clean: Remove patents with missing titles
    before = len(chunk)
    chunk = chunk[chunk['patent_title'].notna()]
    chunk = chunk[chunk['patent_title'] != '']
    removed_no_title += before - len(chunk)
    
    # Clean: Add abstract
    chunk["abstract"] = chunk["patent_id"].map(abstract_dict)
    
    # Clean: Extract year from date
    chunk["year"] = pd.to_datetime(
        chunk["patent_date"], errors="coerce"
    ).dt.year
    
    # Clean: Remove patents with invalid years (before 1976 or after 2025)
    before = len(chunk)
    chunk = chunk[chunk['year'].between(1976, 2025)]
    removed_bad_date += before - len(chunk)
    
    # Clean: Rename columns for consistency
    chunk = chunk.rename(columns={
        "patent_title": "title",
        "patent_date": "filing_date"
    })
    
    chunk = chunk[["patent_id", "title", "abstract", "filing_date", "year"]]
    
    # Write incrementally
    if first_chunk:
        chunk.to_csv(patent_output, index=False)
        first_chunk = False
    else:
        chunk.to_csv(patent_output, mode="a", header=False, index=False)
    
    total_patents += len(chunk)

print(f"   ✅ Patents saved: {total_patents:,} rows")
print(f"   📊 Cleaning stats:")
print(f"      - Removed patents with no title: {removed_no_title:,}")
print(f"      - Removed patents with invalid dates: {removed_bad_date:,}")

# Free memory
del abstract_dict

# =========================================================
# CLEANING STEP 3: Clean inventors
# =========================================================
print("\n👨‍🔬 CLEANING STEP 3: Cleaning inventors table")

inventor_output = CLEAN_DIR / "clean_inventors.csv"
inventor_dict = {}
total_inventor_records = 0

for chunk in pd.read_csv(
    RAW_DIR / "g_inventor_disambiguated.tsv",
    sep="\t",
    usecols=["inventor_id", "disambig_inventor_name_first", "disambig_inventor_name_last"],
    chunksize=500000
):
    # Clean: Create full name, handle missing parts
    chunk["name"] = (
        chunk["disambig_inventor_name_first"].fillna("") + " " +
        chunk["disambig_inventor_name_last"].fillna("")
    ).str.strip()
    
    # Clean: Remove empty names
    chunk = chunk[chunk['name'] != '']
    
    # Clean: Remove duplicate inventor_ids (keep first)
    chunk = chunk.drop_duplicates(subset=['inventor_id'], keep='first')
    
    inventor_dict.update(dict(zip(chunk["inventor_id"], chunk["name"])))
    total_inventor_records += len(chunk)

clean_inventors = pd.DataFrame([
    {"inventor_id": k, "name": v, "country": None}
    for k, v in inventor_dict.items()
])

clean_inventors.to_csv(inventor_output, index=False)
print(f"   ✅ Inventors saved: {len(clean_inventors):,} unique inventors")

# =========================================================
# CLEANING STEP 4: Clean companies
# =========================================================
print("\n🏢 CLEANING STEP 4: Cleaning companies table")

company_output = CLEAN_DIR / "clean_companies.csv"
company_dict = {}

for chunk in pd.read_csv(
    RAW_DIR / "g_assignee_disambiguated.tsv",
    sep="\t",
    usecols=[
        "assignee_id",
        "disambig_assignee_organization",
        "disambig_assignee_individual_name_first",
        "disambig_assignee_individual_name_last"
    ],
    chunksize=500000
):
    # Clean: Prefer organization name, fall back to individual name
    org = chunk["disambig_assignee_organization"].fillna("")
    individual = (
        chunk["disambig_assignee_individual_name_first"].fillna("") + " " +
        chunk["disambig_assignee_individual_name_last"].fillna("")
    ).str.strip()
    
    # Clean: Use organization if available, otherwise individual
    chunk["name"] = org.where(org != "", individual)
    
    # Clean: Remove empty names
    chunk = chunk[chunk['name'] != '']
    
    # Clean: Remove duplicate assignee_ids
    chunk = chunk.drop_duplicates(subset=['assignee_id'], keep='first')
    
    company_dict.update(dict(zip(chunk["assignee_id"], chunk["name"])))

clean_companies = pd.DataFrame([
    {"company_id": k, "name": v}
    for k, v in company_dict.items()
])

clean_companies.to_csv(company_output, index=False)
print(f"   ✅ Companies saved: {len(clean_companies):,} unique companies")

# =========================================================
# CLEANING STEP 5: Create relationships (normalization)
# =========================================================
print("\n🔗 CLEANING STEP 5: Creating relationships table (database normalization)")

rel_output = CLEAN_DIR / "clean_relationships.csv"

# Load inventor-patent relationships
print("   Loading inventor-patent links...")
inventor_links = pd.read_csv(
    RAW_DIR / "g_inventor_disambiguated.tsv",
    sep="\t",
    usecols=["patent_id", "inventor_id"],
    dtype=str
)

# Load company-patent relationships
print("   Loading company-patent links...")
company_links = pd.read_csv(
    RAW_DIR / "g_assignee_disambiguated.tsv",
    sep="\t",
    usecols=["patent_id", "assignee_id"],
    dtype=str
)
company_links = company_links.rename(columns={"assignee_id": "company_id"})

# Clean: Remove duplicates in relationships
inventor_links = inventor_links.drop_duplicates()
company_links = company_links.drop_duplicates()

# Merge into single relationships table
print("   Merging relationships...")
relationships = inventor_links.merge(
    company_links,
    on="patent_id",
    how="outer"
)

relationships.to_csv(rel_output, index=False)
print(f"   ✅ Relationships saved: {len(relationships):,} rows")

# =========================================================
# CLEANING SUMMARY
# =========================================================
print("\n" + "=" * 60)
print("CLEANING COMPLETE - SUMMARY")
print("=" * 60)
print(f"📁 Output files saved to: {CLEAN_DIR}")
print(f"   - clean_patents.csv: {total_patents:,} rows")
print(f"   - clean_inventors.csv: {len(clean_inventors):,} rows")
print(f"   - clean_companies.csv: {len(clean_companies):,} rows")
print(f"   - clean_relationships.csv: {len(relationships):,} rows")
print("\n✅ Cleaning operations performed:")
print("   ✓ Handled missing values (NULLs, empty strings)")
print("   ✓ Removed duplicate records")
print("   ✓ Extracted year from date field")
print("   ✓ Merged abstract text with patent records")
print("   ✓ Standardized column names")
print("   ✓ Filtered out invalid data")
print("   ✓ Created normalized relationships table")
print("=" * 60)