import pandas as pd
from pathlib import Path

RAW_DIR = Path("data")
CLEAN_DIR = Path("data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 500000

print("🚀 Starting data cleaning pipeline (optimized for large data)...")

# =========================================================
# STEP 1: Load abstracts into dictionary (fast lookup)
# =========================================================
print("\n📘 Step 1/5: Building abstract lookup...")

abstract_dict = {}

for chunk in pd.read_csv(
    RAW_DIR / "g_patent_abstract.tsv",
    sep="\t",
    usecols=["patent_id", "patent_abstract"],
    chunksize=CHUNK_SIZE
):
    abstract_dict.update(dict(zip(chunk["patent_id"], chunk["patent_abstract"])))

print(f"✅ Loaded {len(abstract_dict):,} abstracts")


# =========================================================
# STEP 2: Process patents (write in chunks)
# =========================================================
print("\n📄 Step 2/5: Processing patents...")

patent_output = CLEAN_DIR / "clean_patents.csv"

first_chunk = True

for i, chunk in enumerate(pd.read_csv(
    RAW_DIR / "g_patent.tsv",
    sep="\t",
    usecols=["patent_id", "patent_title", "patent_date"],
    chunksize=CHUNK_SIZE
)):
    # Add abstract
    chunk["abstract"] = chunk["patent_id"].map(abstract_dict)

    # Extract year
    chunk["year"] = pd.to_datetime(
        chunk["patent_date"], errors="coerce"
    ).dt.year

    # Rename columns
    chunk = chunk.rename(columns={
        "patent_title": "title",
        "patent_date": "filing_date"
    })

    chunk = chunk[
        ["patent_id", "title", "abstract", "filing_date", "year"]
    ]

    # Write incrementally
    if first_chunk:
        chunk.to_csv(patent_output, index=False)
        first_chunk = False
    else:
        chunk.to_csv(patent_output, mode="a", header=False, index=False)

    print(f"  Processed {(i+1)*CHUNK_SIZE:,} patents...", end="\r")

print("\n✅ Patents saved")


# Free memory
del abstract_dict


# =========================================================
# STEP 3: Process inventors
# =========================================================
print("\n👨‍🔬 Step 3/5: Processing inventors...")

inventor_output = CLEAN_DIR / "clean_inventors.csv"

inventor_dict = {}

for chunk in pd.read_csv(
    RAW_DIR / "g_inventor_disambiguated.tsv",
    sep="\t",
    usecols=[
        "inventor_id",
        "disambig_inventor_name_first",
        "disambig_inventor_name_last"
    ],
    chunksize=CHUNK_SIZE
):
    chunk["name"] = (
        chunk["disambig_inventor_name_first"].fillna("") + " " +
        chunk["disambig_inventor_name_last"].fillna("")
    ).str.strip()

    inventor_dict.update(dict(zip(chunk["inventor_id"], chunk["name"])))

    print(f"  Found {len(inventor_dict):,} inventors...", end="\r")

clean_inventors = pd.DataFrame([
    {"inventor_id": k, "name": v, "country": None}
    for k, v in inventor_dict.items()
])

clean_inventors.to_csv(inventor_output, index=False)

print(f"\n✅ Inventors saved ({len(clean_inventors):,})")


# =========================================================
# STEP 4: Process companies
# =========================================================
print("\n🏢 Step 4/5: Processing companies...")

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
    chunksize=CHUNK_SIZE
):
    org = chunk["disambig_assignee_organization"].fillna("")

    individual = (
        chunk["disambig_assignee_individual_name_first"].fillna("") + " " +
        chunk["disambig_assignee_individual_name_last"].fillna("")
    ).str.strip()

    chunk["name"] = org.where(org != "", individual)

    company_dict.update(dict(zip(chunk["assignee_id"], chunk["name"])))

    print(f"  Found {len(company_dict):,} companies...", end="\r")

clean_companies = pd.DataFrame([
    {"company_id": k, "name": v}
    for k, v in company_dict.items()
])

clean_companies.to_csv(company_output, index=False)

print(f"\n✅ Companies saved ({len(clean_companies):,})")


# =========================================================
# STEP 5: Build relationships table (CRITICAL)
# =========================================================
print("\n🔗 Step 5/5: Building relationships...")

rel_output = CLEAN_DIR / "clean_relationships.csv"

first_chunk = True

for chunk in pd.read_csv(
    RAW_DIR / "g_inventor_disambiguated.tsv",
    sep="\t",
    usecols=["patent_id", "inventor_id"],
    chunksize=CHUNK_SIZE
):
    chunk["company_id"] = None

    if first_chunk:
        chunk.to_csv(rel_output, index=False)
        first_chunk = False
    else:
        chunk.to_csv(rel_output, mode="a", header=False, index=False)

print("  ✔ inventor relationships done")

for chunk in pd.read_csv(
    RAW_DIR / "g_assignee_disambiguated.tsv",
    sep="\t",
    usecols=["patent_id", "assignee_id"],
    chunksize=CHUNK_SIZE
):
    chunk = chunk.rename(columns={"assignee_id": "company_id"})
    chunk["inventor_id"] = None

    chunk = chunk[["patent_id", "inventor_id", "company_id"]]

    chunk.to_csv(rel_output, mode="a", header=False, index=False)

print("  ✔ company relationships done")

print("\n🎉 ALL DONE!")
print(f"Clean files saved in: {CLEAN_DIR}")
