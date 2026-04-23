#!/usr/bin/env python3
"""
Generate LaTeX table from combined aggregated statistics with 95% CI.
"""

import pandas as pd
from pathlib import Path
import argparse

# Parent-Parent labels
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

labels_misspecification_gpt54 = [
    "exp_sp_owner_expenditure_gpt54_25_5",
    "exp_sp_majorcards_dependents_gpt54_25_5",
    "exp_sp_owner_share_gpt54_25_5",
    "exp_sp_majorcards_selfemp_gpt54_25_5",
]


PREDEFINED_LABEL_SETS = {
    "parent_parent_prompts": labels_parent_parent_prompts,
    "direct_estimation_gpt54": labels_direct_estimation_gpt54,
    "misspecification_gpt54": labels_misspecification_gpt54,
}


# Model name mapping
MODEL_MAP = {
    "llama31": "Llama 3.1 8B",
    "llama33": "Llama 3.3 70B",
    "gemini25": "Gemini 2.5 Flash",
    "gpt54": "GPT-5.4",
}

# DAG name mapping
DAG_MAP = {
    "cac": "cachexia",
    "exp": "expenditure",
    "foo": "foodsecurity",
    "alg": "algal2",
    "lex": "lexical",
    "liq": "liquefaction",
    "sto": "stocks",
}

def parse_label(label):
    """Extract DAG and model from labels like 'pp_cac_llama31_25_5' or 'cac_gpt54_25_5'."""
    parts = label.split('_')

    # Handle 'pp_dag_model_...' format
    if len(parts) >= 3 and parts[0] == 'pp':
        dag_code = parts[1]
        model_code = parts[2]
    # Handle 'dag_model_...' format
    elif len(parts) >= 2:
        dag_code = parts[0]
        model_code = parts[1]
    else:
        raise ValueError(f"Label '{label}' has an unsupported format.")

    dag_name = DAG_MAP.get(dag_code, dag_code)
    model_name = MODEL_MAP.get(model_code, model_code)

    return model_name, dag_name

def format_with_ci(mean, ci, precision=4):
    """Format value with 95% CI as: mean ± ci"""
    format_str = f"{{:.{precision}f}}"
    mean_str = format_str.format(mean)
    ci_str = format_str.format(ci)
    return f"${mean_str} \\pm {ci_str}$"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate LaTeX table rows from combined aggregated stats CSV."
    )
    parser.add_argument(
        "--predefined_label_set",
        choices=sorted(PREDEFINED_LABEL_SETS.keys()),
        required=True,
        help="Predefined label set used for labels and default I/O naming.",
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=None,
        help="Optional override input CSV path. Default: output/{set}_combined_aggregated_stats.csv",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help="Optional override output CSV path. Default: output/{set}_latex_table_stats.csv",
    )
    parser.add_argument(
        "--output-latex",
        type=Path,
        default=None,
        help="Optional override output .tex path. Default: output/{set}_latex_table_stats.tex",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        default=None,
        help="Optional explicit label list to include and order labels.",
    )
    return parser.parse_args()

def main():
    args = parse_args()

    set_name = args.predefined_label_set
    input_file = args.input_file or Path(f"output/{set_name}_combined_aggregated_stats.csv")
    output_csv = args.output_csv or Path(f"output/{set_name}_latex_table_stats.csv")
    output_latex = args.output_latex or Path(f"output/{set_name}_latex_table_stats.tex")

    # Read the combined CSV
    df = pd.read_csv(input_file)
    
    # Pivot the data to have one row per label with metrics as columns
    metrics_of_interest = [
        'l2_norm',
        'l2_norm_normalized',
        'l2_norm_normalized_without_single_parent_edges',
        'relative_order_count'
    ]
    
    results = []

    if args.labels is not None:
        labels_to_process = args.labels
    else:
        labels_to_process = PREDEFINED_LABEL_SETS[set_name]
    
    # Group by label
    for label in labels_to_process:
        label_data = df[df['label'] == label]
        if label_data.empty:
            print(f"WARNING: Label '{label}' not found in input file. Skipping.")
            continue
        model_name, dag_name = parse_label(label)
        
        row = {
            'Model': model_name,
            'DAG': dag_name,
        }
        
        # Extract each metric
        for metric in metrics_of_interest:
            metric_row = label_data[label_data['Metric'] == metric]
            if not metric_row.empty:
                mean = metric_row['Mean'].values[0]
                ci = metric_row['CI_95_Range'].values[0]
                
                # Format with 4 decimal places
                row[metric] = format_with_ci(mean, ci, precision=4)
            else:
                row[metric] = "N/A"
        
        results.append(row)
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Rename columns for LaTeX table
    results_df.columns = [
        'Model',
        'DAG',
        'L2 Norm',
        'L2 Norm Normalized',
        'L2 Norm Normalized (No Single Parent)',
        'Relative Count'
    ]
    
    # Sort by DAG in the requested order, then by Model
    dag_order = ["cachexia", "expenditure", "foodsecurity", "algal2", "lexical", "liquefaction", "stocks"]
    model_order = ["Gemini 2.5 Flash", "Llama 3.1 8B", "Llama 3.3 70B", "GPT-5.4"]
    results_df["DAG"] = pd.Categorical(results_df["DAG"], categories=dag_order, ordered=True)
    results_df["Model"] = pd.Categorical(results_df["Model"], categories=model_order, ordered=True)
    results_df = results_df.sort_values(["DAG", "Model"]).reset_index(drop=True)
    
    # Save to CSV
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_csv, index=False)
    print(f"✓ Saved CSV to: {output_csv}")
    
    # Generate LaTeX table rows
    output_latex.parent.mkdir(parents=True, exist_ok=True)
    with open(output_latex, 'w') as f:
        num_rows = len(results_df)
        for idx, row in results_df.iterrows():
            latex_row = (
                f"{row['Model']:<20} & {row['DAG']:<15} & "
                f"{row['L2 Norm']} & "
                f"{row['L2 Norm Normalized']} & "
                f"{row['L2 Norm Normalized (No Single Parent)']} & "
                f"{row['Relative Count']} \\\\"
            )
            f.write(latex_row + "\n")
            print(latex_row)
            # Add \addlinespace after the last row for each DAG
            is_last = idx == num_rows - 1
            curr_dag = row['DAG']
            next_dag = results_df.iloc[idx + 1]['DAG'] if not is_last else None
            if is_last or curr_dag != next_dag:
                f.write("\\addlinespace\n")
    
    print(f"\n✓ Saved LaTeX to: {output_latex}")
    print(f"  Total rows: {len(results_df)}")

if __name__ == "__main__":
    main()
