#!/usr/bin/env python3
"""
Generate LaTeX table from combined aggregated statistics with 95% CI.
"""

import pandas as pd
from pathlib import Path

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
]


# Model name mapping
MODEL_MAP = {
    "llama31": "Llama 3.1 8B",
    "llama33": "Llama 3.3 70B",
    "gemini25": "Gemini 2.5 Flash",
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
    """Extract DAG and model from label like 'pp_cac_llama31_25_5'"""
    parts = label.split('_')
    
    # Handle 'pp_dag_model_...' format
    if parts[0] == 'pp':
        dag_code = parts[1]
        model_code = parts[2]
    else:
        raise ValueError(f"Label '{label}' does not have 'pp_' prefix. Only parent-parent labels are handled by this script.")
    
    dag_name = DAG_MAP.get(dag_code, dag_code)
    model_name = MODEL_MAP.get(model_code, model_code)
    
    return model_name, dag_name

def format_with_ci(mean, ci, precision=4):
    """Format value with 95% CI as: mean ± ci"""
    format_str = f"{{:.{precision}f}}"
    mean_str = format_str.format(mean)
    ci_str = format_str.format(ci)
    return f"${mean_str} \\pm {ci_str}$"

def main():
    # Read the combined CSV
    input_file = Path("output/pp_combined_aggregated_stats.csv")
    df = pd.read_csv(input_file)
    
    # Pivot the data to have one row per label with metrics as columns
    metrics_of_interest = [
        'l2_norm',
        'l2_norm_normalized',
        'l2_norm_normalized_without_single_parent_edges',
        'relative_order_count'
    ]
    
    results = []
    
    # Group by label
    for label in df['label'].unique():
        label_data = df[df['label'] == label]
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
    dag_order = ["cachexia", "expenditure", "foodsecurity", "lexical", "liquefaction", "stocks"]
    model_order = ["Llama 3.1 8B", "Llama 3.3 70B", "Gemini 2.5 Flash"]
    results_df["DAG"] = pd.Categorical(results_df["DAG"], categories=dag_order, ordered=True)
    results_df["Model"] = pd.Categorical(results_df["Model"], categories=model_order, ordered=True)
    results_df = results_df.sort_values(["DAG", "Model"]).reset_index(drop=True)
    
    # Save to CSV
    output_csv = Path("output/pp_latex_table_stats.csv")
    results_df.to_csv(output_csv, index=False)
    print(f"✓ Saved CSV to: {output_csv}")
    
    # Generate LaTeX table rows
    output_latex = Path("output/pp_latex_table_stats.tex")
    with open(output_latex, 'w') as f:
        for _, row in results_df.iterrows():
            latex_row = (
                f"{row['Model']:<20} & {row['DAG']:<15} & "
                f"{row['L2 Norm']} & "
                f"{row['L2 Norm Normalized']} & "
                f"{row['L2 Norm Normalized (No Single Parent)']} & "
                f"{row['Relative Count']} \\\\"
            )
            f.write(latex_row + "\n")
            print(latex_row)
    
    print(f"\n✓ Saved LaTeX to: {output_latex}")
    print(f"  Total rows: {len(results_df)}")

if __name__ == "__main__":
    main()
