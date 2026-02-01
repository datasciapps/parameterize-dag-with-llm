#!/usr/bin/env python3
"""
Concatenate all aggregated_stats CSV files from bulk quick_result runs.
"""

import pandas as pd
import glob
from pathlib import Path

# Labels from bulk_quick_result.sh
labels = [
    "foo_llama31_25_5",
    "foo_llama33_25_5",
    "foo_gemini25_25_5",
    # "alg_llama31_25_5",  # Skipped - no successful runs
    "alg_llama33_25_5",
    "alg_gemini25_25_5",
    "lex_llama31_25_5",
    "lex_llama33_25_5",
    "lex_gemini25_25_5",
    "liq_llama31_25_5",
    "liq_llama33_25_5",
    "liq_gemini25_25_5",
    "sto_llama31_25_5",
    "sto_llama33_25_5",
    "sto_gemini25_25_5",
]

def main():
    output_dir = Path("output")
    all_dfs = []
    
    print("Looking for aggregated_stats CSV files...")
    
    for label in labels:
        # Find CSV files matching the pattern: *_{label}_aggregated_stats.csv
        pattern = f"*_{label}_aggregated_stats.csv"
        matching_files = list(output_dir.glob(pattern))
        
        if matching_files:
            # Sort by filename (timestamp) and take the most recent
            matching_files.sort(reverse=True)
            latest_file = matching_files[0]
            
            print(f"  Loading {label}: {latest_file.name}")
            df = pd.read_csv(latest_file)
            
            # Add a column to identify the source label
            df['label'] = label
            
            all_dfs.append(df)
        else:
            print(f"  WARNING: No file found for {label}")
    
    if not all_dfs:
        print("\nERROR: No CSV files found!")
        return
    
    # Concatenate all dataframes
    print(f"\nConcatenating {len(all_dfs)} files...")
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Save to output file
    output_file = output_dir / "combined_aggregated_stats.csv"
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Successfully saved combined statistics to: {output_file}")
    print(f"  Total rows: {len(combined_df)}")
    print(f"  Columns: {list(combined_df.columns)}")

if __name__ == "__main__":
    main()
