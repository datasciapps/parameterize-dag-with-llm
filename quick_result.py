"""quick_result.py

Utility script to quickly aggregate and visualize LLM evaluation
statistics produced by the main pipeline.

What it does
- Searches the `./output` directory for CSV files matching
    the pattern `*gt_llm_stat_df*.csv`.
- Reads and concatenates those CSVs into a single Pandas
    DataFrame (adds a `source_file` column to identify origin).
- Computes mean and standard deviation for a set of L2-norm
    metrics defined in `STAT_COLUMNS`.
- Produces and saves a bar plot with error bars (`statistics_bar_plot.png`)
    and per-column distribution histograms named
    `distribution_plot_<column>.png` inside the `output` directory.

Usage
- Run as a script: `python quick_result.py` from the repository root.
- Ensure the `output` directory exists and contains the expected
    CSV files. Requires `pandas` and `matplotlib`.
"""

import pandas as pd
from pathlib import Path
import re
import matplotlib.pyplot as plt

# --- Configuration ---
# Set the base directory and the pattern for the files you want to find
BASE_DIR = Path("./output")
SEARCH_PATTERN = "*gt_llm_stat_df*.csv"

# Columns for which to calculate statistics
STAT_COLUMNS = [
    'l2_norm',
    'l2_norm_normalized',
    'l2_norm_normalized_without_single_parent_edges'
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
        f for f in BASE_DIR.iterdir()
        if f.is_file() and f.match(SEARCH_PATTERN)
    ]
    
    if not matching_files:
        print("No matching files found.")
        return []

    # 2. Define the sorting key (extract the number before the extension)
    def extract_sort_key(file_path: Path):
        """Extracts the numerical ID for sorting (e.g., '12' from '..._12.csv')."""
        match = re.search(r'_(\d+)\.csv$', file_path.name)
        if match:
            return int(match.group(1))
        return float('inf')

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
            df['source_file'] = file.name
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

def calculate_and_print_statistics(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
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
            
            # Print the results
            print(f"**Column: {col}**")
            print(f"  - Mean ($\mu$): {mean_val:.4f}")
            print(f"  - Std Dev ($\sigma$): {std_val:.4f}")

            # Collect data for plotting
            stats_data.append({
                'Metric': col,
                'Mean': mean_val,
                'StdDev': std_val
            })
        else:
            print(f"Warning: Column '{col}' not found in the combined data. Skipping.")
    
    return pd.DataFrame(stats_data)

def create_bar_plot(stats_df: pd.DataFrame):
    """Generates a bar plot with error bars for the statistics and saves it."""
    
    if stats_df.empty:
        print("Cannot create plot: Statistics data is empty.")
        return

    plt.figure(figsize=(10, 6))
    
    # Create the bar plot with StdDev as error bars (yerr)
    plt.bar(
        stats_df['Metric'],
        stats_df['Mean'],
        yerr=stats_df['StdDev'],
        capsize=5,  # Size of the error bar caps
        color=['skyblue', 'lightcoral', 'lightgreen']
    )
    
    # Labels and Title
    plt.title('Mean L2 Norm Metrics with Standard Deviation Error Bars')
    plt.ylabel('Mean Value')
    plt.xlabel('Metric')
    
    # Rotate x-labels for better readability of long names
    plt.xticks(rotation=15, ha='right')
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save the plot to the output directory
    plot_filename = BASE_DIR / "statistics_bar_plot.png"
    plt.savefig(plot_filename)
    plt.close()
    print(f"\nBar plot successfully saved to: {plot_filename}")

def create_distribution_plots(df: pd.DataFrame, columns: list[str]):
    """Generates and saves a histogram for each specified column."""
    if df.empty:
        print("Cannot create distribution plots: DataFrame is empty.")
        return

    print("\n--- Generating Distribution Plots ---")
    
    for col in columns:
        if col in df.columns:
            # Create a new figure for each plot
            plt.figure(figsize=(10, 6))
            
            # Dropna() is used to ignore missing values when plotting the distribution
            data_to_plot = df[col].dropna()
            
            # Check if data_to_plot is empty after dropping NaNs
            if data_to_plot.empty:
                 print(f"  > Warning: Column '{col}' has no valid (non-NaN) data for plotting. Skipping.")
                 plt.close()
                 continue
                 
            # Use plt.hist() for a basic histogram
            plt.hist(data_to_plot, bins=50, edgecolor='black', alpha=0.7)
            
            # Calculate mean and std dev to add to the plot title/legend
            mean_val = data_to_plot.mean()
            std_val = data_to_plot.std()

            # Labels and Title
            plt.title(f'Distribution of {col}\nMean: {mean_val:.4f}, Std Dev: {std_val:.4f}')
            plt.xlabel(col)
            plt.ylabel('Frequency (Count)')
            
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # Save the plot
            # Create a safe filename 
            safe_col_name = col.replace('.', '_') 
            plot_filename = BASE_DIR / f"distribution_plot_{safe_col_name}.png"
            plt.savefig(plot_filename)
            plt.close() # Close the figure to free up memory
            print(f"  > Distribution plot for '{col}' saved to: {plot_filename.name}")
            
        else:
            print(f"  > Warning: Column '{col}' not found for distribution plot. Skipping.")


# --- Main Execution ---

if __name__ == "__main__":
    
    # 1. Get the list of files, sorted numerically
    files_to_process = get_sorted_files()
    
    # 2. Combine the data
    final_dataframe = combine_csv_files(files_to_process)
    
    # 3. Calculate statistics
    stats_df = pd.DataFrame()
    if not final_dataframe.empty:
        stats_df = calculate_and_print_statistics(final_dataframe, STAT_COLUMNS)
    
    # 4. Create and save the bar plot (RE-INCLUDED)
    if not stats_df.empty:
        create_bar_plot(stats_df)
        
    # 5. Create and save the distribution plots
    if not final_dataframe.empty:
        create_distribution_plots(final_dataframe, STAT_COLUMNS)