"""one_way_anova.py

Command-line utility to perform a one-way ANOVA on a specified
metric/column across three archived result directories.

What it does
- Searches the `output/archive_a`, `output/archive_b`, and
    `output/archive_c` directories for CSV files matching the
    pattern `*gt_llm_stat*.csv`.
- Extracts the value of a user-specified column (the first row
    in each CSV) from each matching file and aggregates those
    values per archive into three groups.
- Asserts that each group has the expected sample size
    (`--n_expected`, default 25) and then performs a one-way ANOVA
    using SciPy's `f_oneway` to test for differences between groups.
- Prints summary statistics and the ANOVA F-statistic and p-value.

Usage examples
```
 python one_way_anova.py --key l2_norm
 python one_way_anova.py --key 12_norm_normalized
 python one_way_anova.py --key l2_norm_normalized
 python one_way_anova.py --key l2_norm_normalized_without_single_parent_edges
```

Notes
- Run from the repository root so the relative `output` directory is
    accessible. Requires `pandas`, `scipy`, and `numpy` installed.
"""

import os
import glob
import pandas as pd
from scipy import stats
import numpy as np
import argparse  # New import for command-line arguments

# --- Configuration ---
FILENAME_PATTERN = "*gt_llm_stat*.csv"
# ---------------------


def extract_key_value(directory_path, key_column):
    """
    Finds all CSV files matching the FILENAME_PATTERN in the given directory,
    extracts the value from the specified key_column from the single row of
    each file, and returns them as a list.
    """
    key_values = []

    # Construct the full pattern to search for
    search_path = os.path.join(directory_path, FILENAME_PATTERN)

    # Use glob to find all matching files
    file_list = glob.glob(search_path)

    print(f"--- Processing directory: {directory_path} ---")

    if not file_list:
        print(f"No files found matching '{FILENAME_PATTERN}' in '{directory_path}'.")
        return []

    for file_path in file_list:
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)

            # Check if the required column exists
            if key_column not in df.columns:
                print(
                    f"Warning: Column '{key_column}' not found in {file_path}. Skipping."
                )
                continue

            # Extract the value from the first row
            if len(df) >= 1:
                value = df[key_column].iloc[0]
            else:
                print(f"Warning: File {file_path} is empty. Skipping.")
                continue

            # Ensure the value is numeric
            if pd.api.types.is_numeric_dtype(type(value)):
                key_values.append(value)
            else:
                print(
                    f"Warning: Column value ({value}) in {file_path} is not numeric. Skipping."
                )

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue

    print(
        f"Found {len(key_values)} valid '{key_column}' values using pattern '{FILENAME_PATTERN}'."
    )
    print("-" * (len(directory_path) + 30))
    return key_values


def perform_anova(
    data_a,
    data_b,
    data_c,
    key_column,
    condition_names=["Condition A", "Condition B", "Condition C"],
):
    """
    Performs a one-way ANOVA on the three datasets.
    """

    if not data_a or not data_b or not data_c:
        print("\n--- ANOVA Canceled ---")
        print(
            "ANOVA requires at least one data point for all groups. Check the extraction process."
        )
        return

    print(f"\n--- One-Way ANOVA Results for '{key_column}' ---")

    try:
        # Perform the one-way ANOVA
        f_statistic, p_value = stats.f_oneway(data_a, data_b, data_c)

        print(f"F-statistic: {f_statistic:.4f}")
        print(f"P-value:     {p_value:.4f}")

        alpha = 0.05
        if p_value < alpha:
            print(
                f"\nThe P-value ({p_value:.4f}) is less than the significance level (alpha={alpha})."
            )
            print(
                f"**Conclusion: We reject the null hypothesis.** There is a statistically significant difference in the '{key_column}' means across the three conditions."
            )
        else:
            print(
                f"\nThe P-value ({p_value:.4f}) is greater than the significance level (alpha={alpha})."
            )
            print(
                f"**Conclusion: We fail to reject the null hypothesis.** There is no statistically significant difference in the '{key_column}' means across the three conditions."
            )

    except ValueError as e:
        print(
            f"Error during ANOVA calculation (likely due to insufficient or constant data): {e}"
        )


def main():
    """
    Main function to parse arguments, orchestrate data extraction, assertion, and ANOVA.
    """
    parser = argparse.ArgumentParser(
        description="Perform One-Way ANOVA on a specified column across three archive directories.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Required argument for the column name
    parser.add_argument(
        "--key",
        type=str,
        required=True,
        help="The column name (key) to extract from the CSV files (e.g., 'l2_norm' or 'mse').",
    )

    # Optional argument for expected sample size
    parser.add_argument(
        "--n_expected",
        type=int,
        default=25,
        help="The expected sample size (N) for each condition/archive. (Default: 25)",
    )

    args = parser.parse_args()
    key_column = args.key
    expected_n = args.n_expected

    print(
        f"Starting ANOVA script with column='{key_column}' and expected N={expected_n}."
    )

    # Define the directories
    base_dir = "output"
    condition_dirs = {
        "Condition A": os.path.join(base_dir, "archive_a"),
        "Condition B": os.path.join(base_dir, "archive_b"),
        "Condition C": os.path.join(base_dir, "archive_c"),
    }

    # 1. Data Extraction
    l2_norms_a = extract_key_value(condition_dirs["Condition A"], key_column)
    l2_norms_b = extract_key_value(condition_dirs["Condition B"], key_column)
    l2_norms_c = extract_key_value(condition_dirs["Condition C"], key_column)

    # 2. Sample Size Assertion
    print("\n--- Sample Size Check ---")
    data_groups = {
        "Condition A": l2_norms_a,
        "Condition B": l2_norms_b,
        "Condition C": l2_norms_c,
    }

    # Check that all conditions have the expected sample size
    for name, data in data_groups.items():
        current_n = len(data)
        try:
            assert current_n == expected_n, (
                f"Sample size mismatch in {name}. Expected N={expected_n}, but found N={current_n}."
            )
            print(f"PASS: {name} has the expected sample size of N={expected_n}.")
        except AssertionError as e:
            print(f"FAIL: {e}")
            raise

    # 3. Summary Statistics
    print("\n--- Summary of Extracted Data ---")
    for name, data in data_groups.items():
        if data:
            print(
                f"{name} (N={len(data)}): Mean={np.mean(data):.4f}, Std Dev={np.std(data):.4f}"
            )
        else:
            print(f"{name}: No data extracted.")

    # 4. Perform One-Way ANOVA
    perform_anova(
        l2_norms_a, l2_norms_b, l2_norms_c, key_column, list(condition_dirs.keys())
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as ae:
        print("\n*** Script Halted ***")
        print(
            f"The ANOVA calculation was skipped due to the sample size assertion failure: {ae}"
        )
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
