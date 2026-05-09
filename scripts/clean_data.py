"""
Data cleaning script for SHL Assessment catalog.
Reads raw_data.csv, deduplicates, decodes abbreviations,
standardizes column names, and writes clean_data.csv.
"""

import pandas as pd
import os

# Paths relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw_data.csv")
CLEAN_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "clean_data.csv")

# Decode single-letter test type abbreviations to full names
TYPE_MAP = {
    "A": "Ability",
    "B": "Behavior",
    "C": "Competency",
    "D": "Development",
    "E": "Experience",
    "K": "Knowledge",
    "P": "Personality",
    "S": "Simulation",
}


def decode_test_types(types_str: str) -> str:
    """Convert 'A, B, P' → 'Ability, Behavior, Personality'"""
    if pd.isna(types_str) or not types_str.strip():
        return ""
    codes = [c.strip() for c in types_str.split(",")]
    decoded = [TYPE_MAP.get(c, c) for c in codes]
    return ", ".join(decoded)


def clean_data():
    print(f"📂 Reading raw data from: {RAW_DATA_PATH}")
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"   Raw rows: {len(df)}")

    # Rename columns to clean, standardized names
    df = df.rename(columns={
        "Test Name": "name",
        "URL": "url",
        "Remote Testing": "remote_testing",
        "Adaptive/IRT": "adaptive_irt",
        "Test Types": "test_types",
    })

    # Deduplicate by name + url
    before = len(df)
    df = df.drop_duplicates(subset=["name", "url"], keep="first")
    print(f"   Removed {before - len(df)} duplicate rows → {len(df)} unique rows")

    # Decode test type abbreviations
    df["test_types"] = df["test_types"].apply(decode_test_types)

    # Sort alphabetically by name
    df = df.sort_values("name").reset_index(drop=True)

    # Save
    df.to_csv(CLEAN_DATA_PATH, index=False)
    print(f"✅ Clean data saved to: {CLEAN_DATA_PATH}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Sample row:")
    print(f"   {df.iloc[0].to_dict()}")


if __name__ == "__main__":
    clean_data()
