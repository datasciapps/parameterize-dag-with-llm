"""quick_result.py

Utility script to quickly aggregate and visualize LLM evaluation
statistics produced by the main pipeline.

What it does
- Searches the `./output` directory for CSV files matching
    the pattern `*gt_llm_stat_df*.csv`.
- Reads and concatenates those CSVs into a single Pandas
    DataFrame (adds a `source_file` column to identify origin).
- Computes mean, standard deviation, and 95% confidence interval for
    L2-norm metrics defined in `STAT_COLUMNS`.
- Produces and saves:
    * Bar plot with error bars (`<timestamp>_<label>_statistics_bar_plot.png`)
    * Per-column distribution histograms (`<timestamp>_<label>_distribution_plot_<column>.png`)
    * Aggregated statistics CSV (`<timestamp>_<label>_aggregated_stats.csv`)
- Supports both interactive mode and bulk processing mode.

Usage
Interactive mode:
    python quick_result.py
    - Prompts user to select from available experiment IDs
    - Process single experiment or all experiments

Bulk mode (batch processing):
    python quick_result.py --bulk "ID1,ID2,ID3,..." --label "experiment_name"
    - Process exactly 25 comma-separated experiment IDs
    - Requires --label argument for output file naming
    - Example: python quick_result.py --bulk "20260128120000,20260128130000,..." --label "my_experiment"

Arguments:
    --bulk: Comma-separated list of experiment IDs (14-digit timestamps) to aggregate.
            Must provide exactly 25 IDs.
    --label: Required label for output files when using --bulk mode. Used as suffix
             in output filenames (e.g., {timestamp}_{label}_aggregated_stats.csv).

Output files:
    - {timestamp}_{label}_aggregated_stats.csv: Mean, StdDev, and 95% CI for each metric
    - {timestamp}_{label}_statistics_bar_plot.png: Bar chart with error bars
    - {timestamp}_{label}_distribution_plot_{metric}.png: Histogram for each metric

Requirements:
    pandas, matplotlib, numpy
"""

import pandas as pd
from pathlib import Path
import re
import matplotlib.pyplot as plt
import argparse

# --- Configuration ---
# Set the base directory and the pattern for the files you want to find
BASE_DIR = Path("./output")
SEARCH_PATTERN = "*gt_llm_stat_df*.csv"

# Columns for which to calculate statistics
STAT_COLUMNS = [
    "l2_norm",
    "l2_norm_normalized",
    "l2_norm_normalized_without_single_parent_edges",
    "relative_order_count",  # M4 metric
]

# --- Core Logic Functions ---


def get_sorted_files() -> list[Path]:
    """
    Finds CSV files matching the pattern directly inside the BASE_DIR
    and sorts them based on the ascending numerical occurrence in the filename.
    """
    print(f"Searching for files matching '{SEARCH_PATTERN}' in {BASE_DIR.resolve()}...")

    if not BASE_DIR.is_dir():
        print(f"Error: Directory '{BASE_DIR}' not found. Please create it.")
        return []

    # 1. Find all matching files directly in the output directory
    matching_files = [
        f for f in BASE_DIR.iterdir() if f.is_file() and f.match(SEARCH_PATTERN)
    ]

    if not matching_files:
        print("No matching files found.")
        return []

    # 2. Define the sorting key (extract the number before the extension)
    def extract_sort_key(file_path: Path):
        """Extracts the numerical ID for sorting (e.g., '12' from '..._12.csv')."""
        match = re.search(r"_(\d+)\.csv$", file_path.name)
        if match:
            return int(match.group(1))
        return float("inf")

    # 3. Sort the list of files in ascending order
    sorted_files = sorted(matching_files, key=extract_sort_key)

    print(f"Found {len(sorted_files)} files, sorted by occurrence ID.")
    return sorted_files


def combine_csv_files(files: list[Path]) -> pd.DataFrame:
    """Reads the list of files and combines them into one DataFrame."""
    if not files:
        return pd.DataFrame()

    all_dfs = []
    print("\n--- Files to be combined (Ascending Order) ---")
    for file in files:
        print(f"-> {file.name}")
        try:
            df = pd.read_csv(file)
            if df.empty:
                print(f"  > Warning: File {file.name} is empty and was skipped.")
                continue
            df["source_file"] = file.name
            all_dfs.append(df)
        except Exception as e:
            print(f"Warning: Could not read {file.name}. Error: {e}")

    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        print("\n--- Combined DataFrame---")
        print(combined_df)
        print(f"\nSuccessfully combined data. Total rows: {len(combined_df)}")
        return combined_df
    else:
        print("\nNo valid data could be combined.")
        return pd.DataFrame()


def calculate_and_print_statistics(
    df: pd.DataFrame, columns: list[str]
) -> pd.DataFrame:
    """Calculates, prints, and returns mean and standard deviation for specified columns."""
    if df.empty:
        print("Cannot calculate statistics: DataFrame is empty.")
        return pd.DataFrame()

    print("\n=======================================================")
    print("âœ¨ Aggregate Statistics for Combined Data")
    print("=======================================================")

    stats_data = []

    for col in columns:
        if col in df.columns:
            mean_val = df[col].mean()
            std_val = df[col].std()
            n = df[col].count()
            
            # Calculate 95% confidence interval
            # CI = mean ± (1.96 * std / sqrt(n))
            import numpy as np
            if n > 1:
                ci_range = 1.96 * std_val / np.sqrt(n)
            else:
                ci_range = np.nan

            # Print the results
            print(f"**Column: {col}**")
            print(f"  - Mean ($\mu$): {mean_val:.4f}")
            print(f"  - Std Dev ($\sigma$): {std_val:.4f}")
            if not np.isnan(ci_range):
                print(f"  - 95% CI: {mean_val:.4f} ± {ci_range:.4f}")

            # Collect data for plotting
            stats_data.append({
                "Metric": col, 
                "Mean": mean_val, 
                "StdDev": std_val,
                "CI_95_Range": ci_range
            })

            # Special print for M4 (relative_order_count)
            if col == "relative_order_count":
                print(f"  >> Aggregated M4 (relative_order_count) across runs: Mean = {mean_val:.4f}, Std = {std_val:.4f}")
        else:
            print(f"Warning: Column '{col}' not found in the combined data. Skipping.")

    return pd.DataFrame(stats_data)


def create_bar_plot(stats_df: pd.DataFrame, timestamp: str = None, label: str = None):
    """Generates a bar plot with error bars for the statistics and saves it."""

    if stats_df.empty:
        print("Cannot create plot: Statistics data is empty.")
        return

    plt.figure(figsize=(10, 6))

    # Create the bar plot with StdDev as error bars (yerr)
    plt.bar(
        stats_df["Metric"],
        stats_df["Mean"],
        yerr=stats_df["StdDev"],
        capsize=5,  # Size of the error bar caps
        color=["skyblue", "lightcoral", "lightgreen"],
    )

    # Labels and Title
    plt.title("Mean L2 Norm Metrics with Standard Deviation Error Bars")
    plt.ylabel("Mean Value")
    plt.xlabel("Metric")

    # Rotate x-labels for better readability of long names
    plt.xticks(rotation=15, ha="right")

    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Save the plot to the output directory
    from datetime import datetime
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    if label:
        plot_filename = BASE_DIR / f"{timestamp}_{label}_statistics_bar_plot.png"
    else:
        plot_filename = BASE_DIR / f"{timestamp}_statistics_bar_plot.png"
    plt.savefig(plot_filename)
    plt.close()
    print(f"\nBar plot successfully saved to: {plot_filename}")


def create_distribution_plots(df: pd.DataFrame, columns: list[str], timestamp: str = None, label: str = None):
    """Generates and saves a histogram for each specified column."""
    if df.empty:
        print("Cannot create distribution plots: DataFrame is empty.")
        return

    from datetime import datetime
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    print("\n--- Generating Distribution Plots ---")

    for col in columns:
        if col in df.columns:
            # Create a new figure for each plot
            plt.figure(figsize=(10, 6))

            # Dropna() is used to ignore missing values when plotting the distribution
            data_to_plot = df[col].dropna()

            # Check if data_to_plot is empty after dropping NaNs
            if data_to_plot.empty:
                print(
                    f"  > Warning: Column '{col}' has no valid (non-NaN) data for plotting. Skipping."
                )
                plt.close()
                continue

            # Use plt.hist() for a basic histogram
            # Try 50 bins first, but fall back to dynamic binning if data range is too small
            data_range = data_to_plot.max() - data_to_plot.min()
            num_bins = 50
            if data_range < 0.5:  # If range is very small, use dynamic binning
                num_bins = max(1, int(data_range * 100))
            plt.hist(data_to_plot, bins=num_bins, edgecolor="black", alpha=0.7)

            # Calculate mean and std dev to add to the plot title/legend
            mean_val = data_to_plot.mean()
            std_val = data_to_plot.std()

            # Labels and Title
            plt.title(
                f"Distribution of {col}\nMean: {mean_val:.4f}, Std Dev: {std_val:.4f}"
            )
            plt.xlabel(col)
            plt.ylabel("Frequency (Count)")

            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()

            # Save the plot
            # Create a safe filename
            safe_col_name = col.replace(".", "_")
            if label:
                plot_filename = BASE_DIR / f"{timestamp}_{label}_distribution_plot_{safe_col_name}.png"
            else:
                plot_filename = BASE_DIR / f"{timestamp}_distribution_plot_{safe_col_name}.png"
            plt.savefig(plot_filename)
            plt.close()  # Close the figure to free up memory
            print(f"  > Distribution plot for '{col}' saved to: {plot_filename.name}")

        else:
            print(
                f"  > Warning: Column '{col}' not found for distribution plot. Skipping."
            )


def extract_experiment_ids() -> dict:
    """
    Extracts all unique experiment IDs (timestamps) from gt_llm_stat_df CSV files.
    Returns a dictionary mapping experiment_id -> list of file paths.
    """
    print(f"Searching for experiment IDs in {BASE_DIR.resolve()}...")
    
    if not BASE_DIR.is_dir():
        print(f"Error: Directory '{BASE_DIR}' not found.")
        return {}
    
    # Find all gt_llm_stat_df CSV files
    all_stat_files = [
        f for f in BASE_DIR.iterdir() if f.is_file() and f.match(SEARCH_PATTERN)
    ]
    
    if not all_stat_files:
        print("No experiment files found.")
        return {}
    
    # Extract experiment IDs (timestamps) from filenames
    import re
    experiments = {}
    for file in all_stat_files:
        match = re.search(r"(\d{14})", file.name)  # Match 14-digit timestamp
        if match:
            exp_id = match.group(1)
            if exp_id not in experiments:
                experiments[exp_id] = []
            experiments[exp_id].append(file)
    
    return experiments


def prompt_user_for_experiment(experiments: dict) -> str:
    """
    Displays available experiment IDs and prompts user to choose one.
    Returns the selected experiment ID or 'all' for all experiments.
    """
    if not experiments:
        print("No experiments available.")
        return None
    
    print("\n" + "="*60)
    print("Available Experiment IDs:")
    print("="*60)
    
    sorted_exp_ids = sorted(experiments.keys())
    for idx, exp_id in enumerate(sorted_exp_ids, 1):
        file_count = len(experiments[exp_id])
        print(f"  [{idx}] {exp_id} ({file_count} file{'s' if file_count > 1 else ''})")
    
    print(f"  [0] ALL experiments (aggregate all {len(sorted_exp_ids)} experiments)")
    print("="*60)
    
    while True:
        try:
            choice = input("\nEnter your choice [0-{}]: ".format(len(sorted_exp_ids))).strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return "all"
            elif 1 <= choice_num <= len(sorted_exp_ids):
                return sorted_exp_ids[choice_num - 1]
            else:
                print(f"Invalid choice. Please enter a number between 0 and {len(sorted_exp_ids)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            return None


# --- Main Execution ---

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Aggregate and visualize LLM evaluation statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--bulk",
        type=str,
        help="Comma-separated list of experiment IDs to aggregate (e.g., '20260128120000,20260128130000')"
    )
    parser.add_argument(
        "--label",
        type=str,
        help="Label name for output files (required when using --bulk)"
    )
    args = parser.parse_args()
    
    # Validate that --label is provided when --bulk is used
    if args.bulk and not args.label:
        parser.error("--label is required when using --bulk mode")
    
    # 1. Extract available experiment IDs
    experiments = extract_experiment_ids()
    
    if not experiments:
        print("No experiments found. Exiting.")
        exit(0)
    
    # 2. Determine which experiments to process
    if args.bulk:
        # CLI mode: process specified experiment IDs
        bulk_ids = [exp_id.strip() for exp_id in args.bulk.split(",")]
        
        # Assert that exactly 25 experiment IDs are provided
        assert len(bulk_ids) == 25, f"Bulk mode requires exactly 25 experiment IDs, but {len(bulk_ids)} were provided."
        
        print(f"\nBulk mode: Processing {len(bulk_ids)} specified experiments")
        
        files_to_process = []
        valid_ids = []
        for exp_id in bulk_ids:
            if exp_id in experiments:
                files_to_process.extend(experiments[exp_id])
                valid_ids.append(exp_id)
                print(f"  ✓ {exp_id} ({len(experiments[exp_id])} files)")
            else:
                print(f"  ✗ {exp_id} (not found, skipping)")
        
        if not files_to_process:
            print("\nNo valid experiments found. Exiting.")
            exit(0)
        
        files_to_process = sorted(files_to_process, key=lambda f: f.name)
        selected_exp_id = "bulk_" + "_".join(valid_ids[:3]) + ("_etc" if len(valid_ids) > 3 else "")
        print(f"\nTotal files to process: {len(files_to_process)}")
    else:
        # Interactive mode: prompt user to select
        selected_exp_id = prompt_user_for_experiment(experiments)
        
        if selected_exp_id is None:
            print("No experiment selected. Exiting.")
            exit(0)
        
        # 3. Get the files to process based on user selection
        if selected_exp_id == "all":
            files_to_process = []
            for exp_files in experiments.values():
                files_to_process.extend(exp_files)
            files_to_process = sorted(files_to_process, key=lambda f: f.name)
            print(f"\nProcessing ALL experiments ({len(files_to_process)} files total)")
        else:
            files_to_process = experiments[selected_exp_id]
            print(f"\nProcessing experiment {selected_exp_id} ({len(files_to_process)} files)")
    
    # 4. Combine the data
    final_dataframe = combine_csv_files(files_to_process)

    # 5. Calculate statistics
    stats_df = pd.DataFrame()
    timestamp = selected_exp_id if selected_exp_id not in ["all"] and not selected_exp_id.startswith("bulk_") else None
    label = args.label if args.bulk else None
    
    if not final_dataframe.empty:
        stats_df = calculate_and_print_statistics(final_dataframe, STAT_COLUMNS)

        # Save the aggregated statistics to a timestamped CSV file
        from datetime import datetime
        # Use the selected experiment ID as timestamp, or generate new one for 'all'
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Build filename with label if provided
        if label:
            agg_csv_name = f"{timestamp}_{label}_aggregated_stats.csv"
        else:
            agg_csv_name = f"{timestamp}_aggregated_stats.csv"
        agg_csv_path = BASE_DIR / agg_csv_name
        stats_df.to_csv(agg_csv_path, index=False)
        print(f"\nAggregated statistics saved to: {agg_csv_path}")

    # 6. Create and save the bar plot (RE-INCLUDED)
    if not stats_df.empty:
        create_bar_plot(stats_df, timestamp, label)

    # 7. Create and save the distribution plots
    if not final_dataframe.empty:
        create_distribution_plots(final_dataframe, STAT_COLUMNS, timestamp, label)
