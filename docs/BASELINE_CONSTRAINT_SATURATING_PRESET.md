# Constraint-Saturating Baseline Preset

## Overview

The `baseline/constraint-saturating` preset provides a **deterministic, constraint-aware baseline** for DAG parameterization experiments. Instead of calling a real LLM, it constructs a synthetic structural equation that:

1. starts from an **equal-share** coefficient allocation across direct parents,
2. computes the **induced target range** from parent bounds,
3. **shrinks all parent coefficients by one common factor** if the induced range is too wide, and
4. chooses an intercept that **centers the induced range** inside the target hard constraint.

This makes the baseline substantially more informative than `baseline/zero-coeff`, `baseline/small-coeff`, or `baseline/big-coeff`, while remaining fully deterministic and cheap to run.

This preset is useful for:
- **Constraint-aware comparison**: Measuring how LLM outputs compare against a baseline that already respects the DAG's hard range information
- **Pipeline testing**: Exercising the same parsing, validation, logging, and visualization path without any external API call
- **Interpretability**: Providing a simple baseline that can be explained directly in terms of the existing symbolic validation logic
- **Ablation studies**: Separating gains from hard-constraint awareness from gains due to domain reasoning

## How It Works

### Baseline Construction

When `baseline/constraint-saturating` is selected as the model, the system skips the LLM API call and synthesizes one equation per scenario.

For a target node $Y$ with parents $X_1, \dots, X_k$:

1. **Equal-share initialization**
   - Set each parent coefficient to `1 / k`
   - Set the temporary intercept to `0`

2. **Induced range computation**
   - Reuse the same min/max propagation logic as the validator
   - Compute the induced target range from the parent hard bounds

3. **Global shrink step**
   - If the induced range width is larger than the target hard-constraint width, multiply all parent coefficients by a single scale factor
   - Otherwise keep the equal-share coefficients unchanged

4. **Midpoint-centering intercept**
   - Compute the midpoint of the target hard constraint
   - Compute the midpoint of the scaled parent contribution range
   - Set the intercept so the final predicted range is centered in the target range

### Intuition

The baseline is deliberately simple:
- **all parents are treated symmetrically** at initialization,
- **only one global scale factor** is used,
- **no domain-specific sign or magnitude reasoning** is injected, and
- the procedure is almost the same computation already used in validation.

That is why this preset is a good baseline: it uses structure and constraints, but it does **not** use domain expertise.

## Relationship to the Validation Mechanism

This baseline is closely tied to the existing symbolic validation path in `src/validator_utlity.py`.

### Shared Range Logic

The implementation now exposes:
- `compute_predicted_target_range(...)`
- `compute_range_midpoint(...)`

The baseline generator in `src/llm_integration.py` uses these helpers to synthesize a valid equation, and the normal validator then uses the same range logic again to confirm consistency.

### Why This Is Important

This means the baseline is not a separate hand-written heuristic. It is effectively a **constructive use of the same mechanism** that later checks proposed equations.

In other words:
- **validator**: “Given coefficients, does the induced range fit the hard constraint?”
- **constraint-saturating baseline**: “Choose simple coefficients so the induced range just fits the hard constraint.”

This symmetry makes the baseline easy to explain in papers, slides, and experiment notes.

## Example

Suppose a target variable `Y` has two parents `A` and `B`.

- Parent bounds:
  - `A in [0, 20]`
  - `B in [10, 30]`
- Target bound:
  - `Y in [0, 8]`

The baseline starts with equal-share slopes:

```text
beta_A = 0.5
beta_B = 0.5
```

That induced range is too wide, so both coefficients are scaled down by a common factor of `0.4`:

```text
beta_A = 0.2
beta_B = 0.2
```

The intercept is then chosen to center the result:

```text
Y = -2*1 + 0.2*A + 0.2*B + E_Y
```

This produces an induced range exactly equal to `[0, 8]`.

## Usage

### Basic Command

```bash
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml \
  -m baseline/constraint-saturating \
  -l 1 \
  --loop-retry-max 0 \
  --iterative-budget 1 \
  --label "constraint_saturating_demo"
```

### Parameters

- `-m baseline/constraint-saturating`: Selects the constraint-aware deterministic baseline
- `-l 1`: Number of outer loops to run
- `--loop-retry-max 0`: No retry budget needed for the synthetic baseline path
- `--iterative-budget 1`: Runs the normal validation path so each synthetic equation is checked
- `--label "..."`: Custom experiment label

### Fast Smoke Test

If you want to skip iterative validation and just exercise the generation path:

```bash
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml \
  -m baseline/constraint-saturating \
  -l 1 \
  --loop-retry-max 0 \
  --iterative-budget 0 \
  --label "constraint_saturating_smoke"
```

## Output Structure

Constraint-saturating baseline runs produce the same output artifacts as real LLM runs:

- **CSV outputs** in `output/`
- **Synthetic equations** in `df_llm_resp_df.csv`
- **Parsed coefficients** in `df_coeff_df.csv`
- **Metric summaries** in `df_gt_llm_stat_df_1.csv`
- **Graph snapshots** in `graph_snapshot_1.json`

Because the model name contains `baseline`, the logger will continue tagging experiment identifiers with `BASELINE_`.

## Implementation Details

### Files Involved

1. **`main.py`**
   - Adds `baseline/constraint-saturating` to `MODEL_CONFIGS`
   - Passes `baseline_strategy="constraint-saturating"` through `model_dependent_config`

2. **`src/llm_integration.py`**
   - Adds strategy-based fake baseline generation
   - Implements `_generate_constraint_saturating_baseline(...)`
   - Builds the synthetic equation string returned to the normal parser

3. **`src/validator_utlity.py`**
   - Exposes reusable range computation helpers
   - Keeps the validator and the baseline on the same symbolic range logic
   - Includes a small numeric tolerance to avoid spurious failures on exact boundaries

### Call Flow

```text
main.py (MODEL_CONFIGS["baseline/constraint-saturating"])
  -> llm_dag_parameterizer.py
     -> run_llm_elicitation(..., model_dependent_config={..., "baseline_strategy": "constraint-saturating"})
        -> [BASELINE PATH] build synthetic equation from hard constraints
           -> split_equations_to_terms(...)
           -> convert_terms_to_coeffient_df(...)
           -> symbolic_range_validator(...)
```

## Design Rationale

### Why Equal-Share?

Equal-share initialization gives the baseline a simple default shape that does not privilege one parent over another.

### Why One Common Scale Factor?

Using one common factor makes the baseline easy to interpret:
- if the induced range is already narrow enough, nothing changes,
- if it is too wide, all parent effects are shrunk proportionally.

This is simpler and more defensible than inventing different heuristic magnitudes for different parents.

### Why Recenter the Intercept?

If only the slopes are shrunk, the induced range may be valid but awkwardly placed inside the target interval. Re-centering the intercept makes the baseline use the available target range more sensibly.

## Limitations

This baseline is still intentionally weak compared with a good LLM proposal:

- **No sign inference**: It does not infer whether a parent should be positive or negative
- **No domain asymmetry**: All parents start with equal weight
- **No semantic reasoning**: It uses bounds only, not variable meaning
- **No parent-parent interaction reasoning**: It ignores dependencies among parents when choosing coefficients

So this baseline is best viewed as a **constraint-aware structural baseline**, not a domain-informed model.

## Troubleshooting

### Q: Why can the range be inside the target interval instead of touching both ends exactly?

**A:** If the equal-share initialization is already narrower than the target interval, the common shrink factor remains `1.0`. In that case the baseline is centered but does not need to saturate both boundaries.

### Q: Why is this related to validation rather than a separate heuristic?

**A:** The baseline reuses the same symbolic range propagation routine that validation uses. It is best thought of as “validation logic run in reverse”: find a simple coefficient set that passes the validator.

### Q: Why add a numeric tolerance in validation?

**A:** Floating-point arithmetic can make a value like `10.0` appear as `10.0000000001`. A tiny tolerance prevents exact-on-boundary baseline proposals from failing spuriously.

## Future Extensions

Natural future variants include:
- **signed constraint-saturating baseline**: initialize signs from known monotonicity hints
- **variance-weighted equal-share baseline**: allocate initial coefficient mass by parent range widths
- **oracle-sign baseline**: use ground-truth sign only, but keep baseline magnitude selection deterministic
