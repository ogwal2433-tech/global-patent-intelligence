import pandas as pd

# Check column names in each file
print("=== PATENTS COLUMNS ===")
patents = pd.read_csv("data/g_patent.tsv", sep='\t', nrows=5)
print(patents.columns.tolist())
print("\n=== ABSTRACTS COLUMNS ===")
abstracts = pd.read_csv("data/g_patent_abstract.tsv", sep='\t', nrows=5)
print(abstracts.columns.tolist())
print("\n=== INVENTORS COLUMNS ===")
inventors = pd.read_csv("data/g_inventor_disambiguated.tsv", sep='\t', nrows=5)
print(inventors.columns.tolist())
print("\n=== ASSIGNEES COLUMNS ===")
assignees = pd.read_csv("data/g_assignee_disambiguated.tsv", sep='\t', nrows=5)
print(assignees.columns.tolist())