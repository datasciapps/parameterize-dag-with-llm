# Zero-Coefficient Baseline Preset

## Overview

The `baseline/zero-coeff` preset provides a **null hypothesis baseline** for DAG parameterization experiments. Instead of calling a real LLM, it injects a synthetic structural equation where **all parent coefficients are set to 0.0**.

This preset is useful for:
- **Statistical comparison**: Measuring how much signal real LLM elicitation provides relative to no signal
- **Integration testing**: Quickly testing the full pipeline without waiting for LLM API calls
- **Debugging**: Verifying metric calculations with known, deterministic coefficients
- **Cost control**: Avoiding LLM API charges while running controlled experiments

## How It Works

### Synthetic Response Generation

When `baseline/zero-coeff` is selected as the model, the system:

1. **Skips the LLM API call** entirely
2. **Constructs a fake equation** in the standard format:
   ```
   Y = 0.0*1 + 0.0*parent_1 + 0.0*parent_2 + ... + E_Y
   ```
   where `parent_1, parent_2, ...` are the actual parent variables from the DAG scenario.

3. **Returns the equation** through the same parsing and validation pipeline as real LLM responses

### Example

For a target variable `GDP` with parents `[Population, Investment]`, the synthetic equation is:
```
GDP = 0.0*1 + 0.0*Population + 0.0*Investment + E_GDP
```

All coefficients (intercept `beta_0` and parent slopes) are exactly zero.

## Usage

### Basic Command

```bash
python main.py dags/chachexia1/disease_informed_real_bounds.yaml \
  -m baseline/zero-coeff \
  -l 25 \
  --loop-retry-max 5 \
  --label "cac_zero_baseline_25_5"
```

### Parameters

- `-m baseline/zero-coeff`: Specifies the baseline model (required)
- `-l 25`: Number of parameterization loops (same as real LLM runs)
- `--loop-retry-max 5`: Retry budget (irrelevant for baseline, as it always succeeds on first try)
- `--label "..."`: Custom label for the experiment (optional; automatically tagged with `BASELINE_` prefix in logs)

### Full Example Across Multiple DAGs

```bash
# Run baseline on all 7 DAGs
python main.py dags/chachexia1/disease_informed_real_bounds.yaml -m baseline/zero-coeff -l 25 --label "cac_zero_25_5"
python main.py dags/expenditure/expenditure.yaml -m baseline/zero-coeff -l 25 --label "exp_zero_25_5"
python main.py dags/foodsecurity/foodsecurity.yaml -m baseline/zero-coeff -l 25 --label "foo_zero_25_5"
python main.py dags/algal2/algal2.yaml -m baseline/zero-coeff -l 25 --label "alg_zero_25_5"
python main.py dags/lexical/lexical.yaml -m baseline/zero-coeff -l 25 --label "lex_zero_25_5"
python main.py dags/liquefaction/liquefaction.yaml -m baseline/zero-coeff -l 25 --label "liq_zero_25_5"
python main.py dags/stocks/stocks.yaml -m baseline/zero-coeff -l 25 --label "sto_zero_25_5"
```

## Output Structure

Baseline runs produce the same output structure as real LLM runs:

- **CSV outputs** in `output/` directory with `BASELINE_` prefix in experiment ID
- **Metrics files** (coeff_df, llm_resp_df, gt_llm_stat_df) with all coefficients = 0.0
- **Log files** in `output/logs/` tagged with `BASELINE_`

### Example Output Files

For label `cac_zero_25_5`:
```
output/BASELINE_20260423_123456_cac_zero_25_5/
  ├── df_coeff_df.csv
  ├── df_llm_resp_df.csv
  ├── df_gt_llm_stat_df_1.csv
  └── graph_snapshot_1.json
```

## Metric Values for Baseline

Since all coefficients are 0.0, expected metric values are:

- **M1 (L2 Norm)**: Non-zero (distance from GT coefficients to zero)
- **M2 (L2 Norm Normalized)**: Non-zero (normalized per node)
- **M3 (L2 Norm w/o single-parent edges)**: Non-zero (multi-parent edges only)
- **M4 (Relative Order Count)**: 0 (no parent effect ordering matches)

These serve as the **null hypothesis** for comparison with real LLM results.

## Aggregating Baseline Results

### Using `concatenate_stats.py`

Add baseline labels to a predefined set in `concatenate_stats.py`:

```python
labels_baseline_zero = [
    "cac_zero_25_5",
    "exp_zero_25_5",
    "foo_zero_25_5",
    "alg_zero_25_5",
    "lex_zero_25_5",
    "liq_zero_25_5",
    "sto_zero_25_5",
]

PREDEFINED_LABEL_SETS = {
    # ... existing sets ...
    "baseline_zero": labels_baseline_zero,
}
```

Then aggregate:
```bash
python concatenate_stats.py --predefined_label_set baseline_zero
```

### Generating LaTeX Tables

```bash
python deprecated/generate_latex_table_pp.py --predefined_label_set baseline_zero
```

## Implementation Details

### Files Modified

1. **`main.py`**
   - Added `"baseline/zero-coeff"` entry to `MODEL_CONFIGS` with `"is_fake_baseline": True` flag

2. **`src/llm_integration.py`**
   - Modified `run_llm_elicitation()` to detect `is_fake_baseline` flag
   - Generates synthetic equation with zero coefficients
   - Skips real LLM API call

3. **`src/logging_utility.py`**
   - Added baseline detection: `self.is_baseline = "baseline" in model_name.lower()`
   - Automatically prepends `BASELINE_` to experiment IDs for easy filtering

4. **`src/llm_dag_parameterizer.py`**
   - No changes needed; flag is passed via `model_dependent_config` dictionary

### Call Flow

```
main.py (MODEL_CONFIGS["baseline/zero-coeff"])
  └─> llm_dag_parameterizer.py
       └─> run_llm_elicitation(model_dependent_config={..., "is_fake_baseline": True})
            └─> [BASELINE PATH] Generate synthetic equation
                 └─> [Skip LLM API call]
                      └─> Return DataFrame with zero coefficients
```

## Design Rationale

### Why Not Use a Mock LLM?

A dedicated **baseline/zero-coeff preset** is cleaner than mocking a real LLM because:

- **Explicit**: The name clearly signals "this is a null hypothesis, not a real model"
- **Deterministic**: Always produces identical results (no randomness)
- **No API overhead**: No network calls, timeouts, or rate-limiting logic
- **Isolation**: Real LLM logic remains untouched; baseline logic is isolated in a conditional

### Why Always Zero?

Zero coefficients represent **complete absence of signal**, making this a true null hypothesis:
- Any effect in M1–M4 is purely from GT variability or measurement noise
- Comparing LLM results to this baseline reveals signal quality objectively
- Simple and interpretable: "How much better does the LLM do vs. doing nothing?"

## Troubleshooting

### Q: Why are all metrics non-zero if all coefficients are 0?
**A:** Because metrics compare LLM estimates (zero) to ground truth values (typically non-zero). The L2 distances quantify how far zero is from the GT coefficients.

### Q: Can I use baseline with other scripts?
**A:** Yes, baseline outputs are standard DAG output CSVs. Any script expecting standard output (e.g., `quick_result.py`, `one_way_anova.py`) will work without modification.

### Q: How do I filter baseline runs in downstream analysis?
**A:** Look for `BASELINE_` prefix in experiment IDs, or check the `model_name` column in aggregated CSV files for `baseline/zero-coeff`.

## Future Extensions

Potential variations of the baseline preset:

- **`baseline/random-coeff`**: Random coefficients (uniform or normal)
- **`baseline/gt-coeff`**: Use actual GT coefficients (oracle, upper bound on performance)
- **`baseline/noise-coeff`**: Small random noise added to zero
