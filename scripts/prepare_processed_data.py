import os, sys
import pandas as pd
from pathlib import Path

# make src importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

from src.data.preprocess import preprocess_data
from src.features.build_features import build_features

RAW = PROJECT_ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
OUT = PROJECT_ROOT / "data" / "processed"

# 1) load raw
df = pd.read_csv(RAW)

# 2) preprocess (drops id, fixes TotalCharges, etc.)
df = preprocess_data(df, target_col="Churn")

# 3) ensure target is 0/1 only if still object
if "Churn" in df.columns and df["Churn"].dtype == "object":
    df["Churn"] = df["Churn"].str.strip().map({"No": 0, "Yes": 1}).astype("Int64")

# sanity checks
assert df["Churn"].isna().sum() == 0, "Churn has NaNs after preprocess"
assert set(df["Churn"].unique()) <= {0, 1}, "Churn not 0/1 after preprocess"

# 4) features
df_processed = build_features(df, target_col="Churn")

# 5) save
OUT.mkdir(parents=True, exist_ok=True)

output_file = OUT / "processed_data.csv"

df_processed.to_csv(output_file, index=False)
print(f"✅ Processed dataset saved to {OUT} | Shape: {df_processed.shape}")
print(f"Loaded data from: {RAW}")
print(f"Output directory: {OUT}")
