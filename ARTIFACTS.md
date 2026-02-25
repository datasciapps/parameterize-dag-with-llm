# Experiment Artifacts Documentation

This document describes the logs and artifacts generated during `main.py` execution.

## Overview

When `main.py` runs, it generates multiple types of artifacts to track the parameterization process:
1. **Log files** - Detailed execution logs for each loop
2. **CSV files** - Structured data outputs (LLM responses, coefficients, statistics)
3. **PDF visualizations** - DAG visualizations with effect sizes
4. **JSON snapshots** - Complete graph state and metadata

## Log Files

**Location**: `output/logs/`

**Naming Convention**: `{timestamp}_{label}_loop_{loop_num}.log`

Example: `20260225_142134_module_debug1_loop_1.log`

**Content**:
- Complete console output for each loop iteration
- All print statements from the execution
- Error messages and stack traces (if any)
- Uses `TeeStream` to write to both console and file simultaneously

**Implementation**: 
- Managed by `ExperimentLogger` class in `src/logging_utility.py`
- Creates one log file per loop
- Uses context manager `redirect_output()` to capture stdout/stderr

## Experiment ID

**Format**: `{timestamp}` (e.g., `20260225142134`)

**Generation**: Created at the start of `parameterize_dag()` using `datetime.datetime.now().strftime("%Y%m%d%H%M%S")`

**Usage**: Used as prefix for all artifact filenames to link them to the same experiment run

## CSV Artifacts

All CSV files are saved to `output/` directory with the experiment ID prefix.

### 1. LLM Response DataFrame (`df_llm_resp_df.csv`)

**Content**: Raw LLM responses for each scenario
- `plausibility`: LLM's assessment of plausibility
- `proposed_lin_str_eq`: The linear equation string proposed by LLM

**When Generated**: After each LLM elicitation call via `display()` function

**Append Mode**: Uses append mode, so multiple scenarios accumulate in the same file

### 2. Coefficients DataFrame (`df_coeff_df.csv`)

**Content**: Parsed coefficients from LLM equations
- Columns: `beta_0`, `beta_{parent1}`, `beta_{parent2}`, etc.
- One row per scenario showing the numerical coefficients

**When Generated**: After parsing the LLM equation string via `convert_terms_to_coeffient_df()`

**Append Mode**: Uses append mode, accumulates across scenarios

### 3. Ground Truth vs LLM Statistics (`df_gt_llm_stat_df_{iteration}.csv`)

**Content**: Statistical comparison metrics
- `l2_norm`: L2 norm of differences between LLM and ground truth effects
- `l2_norm_normalized`: L2 norm with node-wise normalization
- `l2_norm_normalized_without_single_parent_edges`: L2 norm excluding single-parent edges
- `relative_order_count`: Count of correct relative ordering of effects
- `total_multi_parent_nodes`: Total nodes with multiple parents

**When Generated**: At the end of `visualize_full_dag_effects()` after computing all statistics

**Iteration Suffix**: Each successful loop creates a new file with iteration number (e.g., `_1`, `_2`)

## PDF Visualizations

### 1. DAG Visualization (`graph_vis_full_dag_{iteration}.pdf`)

**Content**: Graphviz visualization of the complete DAG

**When Generated**: 
- Initial DAG structure: Called at start via `education_wage_dag.visualize_dag(exp_id=exp_id)`
- Final DAG with effects: Called at end via `visualize_full_dag_effects()`

**Features**:
- Node colors indicate validation success:
  - **Lightgreen**: Correct relative ordering of parent effects (for multi-parent nodes)
  - **Lightcoral**: Incorrect relative ordering of parent effects
  - **Lightgray**: Single parent, no parents, or insufficient data
- Edge labels show:
  - `LLM={value}`: LLM-elicited effect size (scientific notation)
  - `GT={value}`: Ground truth effect size (scientific notation)
  - `*` prefix indicates validation failed for that scenario

**Implementation**: Uses `graphviz.Digraph` and saved via `display()` function in `src/custom_display_utility.py`

### 2. Unique File Handling

**Mechanism**: `_unique_path()` function ensures no overwrites
- First file: `{exp_id}graph_vis_full_dag_1.pdf`
- Subsequent files: `_2.pdf`, `_3.pdf`, etc.

## JSON Snapshots

**File**: `graph_snapshot_{iteration}.json`

**Content**: Complete serialized state of the experiment
```json
{
  "all_scenarios": [...],           // All scenario configurations
  "all_coefficients_dfs": [...],    // Coefficient DataFrames as dicts
  "dag_data": {                      // Complete DAG structure
    "all_nodes": [...],
    "raw_edges": [...],
    "node_descriptions": {...},
    "ground_truth_effect_sizes": {...},
    ...
  },
  "all_scenario_validation_success": [...],  // Boolean success per scenario
  "all_effect_sizes_map": {...},    // All LLM-elicited effects
  "llm_effects_by_target": {...},   // Effects grouped by target node
  "gt_effects_by_target": {...},    // Ground truth grouped by target
  "node_colors": {...},              // Visualization colors
  "statistics_label_text": "...",   // Statistics summary text
  "l2_norm_value": ...               // Final L2 norm metric
}
```

**When Generated**: At the end of `visualize_full_dag_effects()` via `export_graph_snapshot_to_json()`

**Purpose**: Enables post-processing analysis and reproduction of visualizations

## File Naming Summary

| Artifact Type | Naming Pattern | Example |
|---------------|----------------|---------|
| Log files | `{timestamp}_{label}_loop_{N}.log` | `20260225_142134_module_debug1_loop_1.log` |
| LLM responses | `{exp_id}df_llm_resp_df.csv` | `20260225142134df_llm_resp_df.csv` |
| Coefficients | `{exp_id}df_coeff_df.csv` | `20260225142134df_coeff_df.csv` |
| Statistics | `{exp_id}df_gt_llm_stat_df_{N}.csv` | `20260225142134df_gt_llm_stat_df_1.csv` |
| DAG PDF | `{exp_id}graph_vis_full_dag_{N}.pdf` | `20260225142134graph_vis_full_dag_1.pdf` |
| JSON snapshot | `{exp_id}graph_snapshot_{N}.json` | `20260225142134graph_snapshot_1.json` |

## Key Implementation Details

### Experiment ID vs Timestamp
- **Experiment ID** (from `ExperimentLogger`): `{timestamp}_{label}` format, used for log filenames
- **exp_id** (from `parameterize_dag`): Just timestamp, used for output artifact filenames
- These are different but both include timestamp for correlation

### Display Function
The `display()` function in `src/custom_display_utility.py` handles both DataFrame and Graphviz objects:
- Prints to console (with optional silence)
- Saves to appropriate format (CSV for DataFrames, PDF for Graphviz)
- Manages file uniqueness via `_unique_path()`
- Supports append mode for accumulating results across scenarios

### Custom JSON Encoder
`CustomJsonEncoder` handles non-serializable types:
- Converts `numpy.float64` to Python `float`
- Converts `set` to `list`
- Converts tuple dictionary keys to strings
