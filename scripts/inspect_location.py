import pandas as pd
from pathlib import Path

RAW_DIR = Path("data")

# Check location file columns
print("Location file columns:")
location_sample = pd.read_csv(RAW_DIR / "g_location_disambiguated.tsv", sep='\t', nrows=5)
print(location_sample.columns.tolist())
print("\nSample data:")
print(location_sample)