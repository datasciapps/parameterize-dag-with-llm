#!/usr/bin/env python3
"""
Concatenate all aggregated_stats CSV files from bulk quick_result runs.
When running quick_result.py, you need to specify consistent labels using --labels.
To create create latex labels, after running this, you need to run another latex script.


In the author's local output/ directory, there are many log files and artifacts with labels.
Currently concatenate_stats.py is hardcoded with such labels. 

For now we try to record the steps for us to obtain tables in our paper as in predefined sets. 

For example,
```
python concatenate_stats.py --predefined_label_set parent_parent_prompts
```

FYI: The previous quick_result, if used with --bulk, then usually 25 runs are garanteed during aggregation. 
Usually you don't need to worry about this as long as concatanate_stats.py is able to find the files.

Also if you aggreate files using quick_result.py multiple times, concatenate_stats.py will pick the most recent one based on filename timestamp

If you want to add a new predefined label set, add entry to PREDEFINED_LABEL_SETS with a list of labels.
"""

import pandas as pd
from pathlib import Path
import argparse


# [Main experiments - direct estimation prompts for seven DAGs]
labels_direct_estimation = [
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

# [Main experiments - misspecification prompts for Expenditure DAG]
labels_misspecification = [
    "exp_sp_owner_expenditure_llama31_25_5",
    "exp_sp_owner_expenditure_llama33_25_5",
    "exp_sp_owner_expenditure_gemini25_25_5",
    "exp_sp_majorcards_dependents_llama31_25_5",
    "exp_sp_majorcards_dependents_llama33_25_5",
    "exp_sp_majorcards_dependents_gemini25_25_5",
    "exp_sp_owner_share_llama31_25_5",
    "exp_sp_owner_share_llama33_25_5",
    "exp_sp_owner_share_gemini25_25_5",
    "exp_sp_majorcards_selfemp_llama31_25_5",
    "exp_sp_majorcards_selfemp_llama33_25_5",
    "exp_sp_majorcards_selfemp_gemini25_25_5",
]


labels_misspecification_gpt54 = [
    "exp_sp_owner_expenditure_gpt54_25_5",
    "exp_sp_majorcards_dependents_gpt54_25_5",
    "exp_sp_owner_share_gpt54_25_5",
    "exp_sp_majorcards_selfemp_gpt54_25_5",
]

# [Appendix - parent-parent effect prompts]
labels_parent_parent_prompts = [
    "pp_cac_llama31_25_5",
    "pp_cac_llama33_25_5",
    "pp_cac_gemini25_25_5",
    "pp_exp_llama31_25_5",
    "pp_exp_llama33_25_5",
    "pp_foo_llama31_25_5",
    "pp_foo_llama33_25_5",
    "pp_lex_llama31_25_5",
    "pp_lex_llama33_25_5",
    "pp_lex_gemini25_25_5",
    "pp_liq_llama31_25_5",
    "pp_liq_llama33_25_5",
    "pp_sto_llama33_25_5",
    "pp_sto_gemini25_25_5",
    # 2nd batch
    "pp_exp_gemini25_25_5",
    "pp_foo_gemini25_25_5",
    "pp_alg_llama31_25_5",
    "pp_alg_gemini25_25_5",
    # 3rd batch
    "pp_alg_llama33_25_5",
    "pp_liq_gemini25_25_5",
    "pp_sto_llama31_25_5"
]


labels_direct_estimation_gpt54 = [
    "cac_gpt54_25_5",
    "exp_gpt54_25_5",
    "foo_gpt54_25_5",
    "alg_gpt54_25_5",
    "lex_gpt54_25_5",
    "liq_gpt54_25_5",
    "sto_gpt54_25_5"
]

labels_milli_cachexia = [
    "mill_cac_gemini25",
    "mill_cac_gpt54",
    "mill_cac_llama31",
    "mill_cac_llama33",
]



PREDEFINED_LABEL_SETS = {
    "direct_estimation": labels_direct_estimation,
    "misspecification": labels_misspecification,
    "parent_parent_prompts": labels_parent_parent_prompts,
    "direct_estimation_gpt54": labels_direct_estimation_gpt54,
    "misspecification_gpt54": labels_misspecification_gpt54,
    "milli_cachexia": labels_milli_cachexia,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Concatenate aggregated stats for a predefined experiment label set."
    )
    parser.add_argument(
        "--predefined_label_set",
        choices=sorted(PREDEFINED_LABEL_SETS.keys()),
        required=True,
        help="Which predefined label set to concatenate.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    labels = PREDEFINED_LABEL_SETS[args.predefined_label_set]

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
    output_file = output_dir / f"{args.predefined_label_set}_combined_aggregated_stats.csv"
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Successfully saved combined statistics to: {output_file}")
    print(f"  Total rows: {len(combined_df)}")
    print(f"  Columns: {list(combined_df.columns)}")

if __name__ == "__main__":
    main()
