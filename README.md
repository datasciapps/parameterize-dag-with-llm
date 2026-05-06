## LLM-SCM Parameterizer

An evaluation pipeline to see given a DAG, how well/poorly LLMs can parameterize SCM/Bayesian Network in linear and continuous domains. 

- The pipeline comes with multiple DAGs and their learned ground-truth parameters thanks to bnRep repository.  
- The LLM calling part is implemented via general instructor package, so you can easily switch LLM to your favorite ones. Structured output, call-retry etc are handled by the instructor package.  
- The codebase is adapted to CLI environment, which will output all the artifacts (csv and pdf) into ./output directory. 


## Project status

The tooling is under active development. Feedback, bug reports, and feature requests are welcome via this GitHub repository.

For DAGs, if you reproduce experiments with DAGs in the paper, please know that they are sourced from MIT-liscenced external repository. Make sure to find correct citations for each DAG. Our repo itself is open-sourced under MIT-liscence as well. For details, please check LISCENCE file in the top level. 

## Setup 

Developer's environment:
> Python 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] on linux

### LLM prerequisite

- Via the instructor package, you can use multiple LLM models from different providers.
- Supported models:
  - `groq/llama-3.1-8b-instant` (Groq provider)
  - `groq/llama-3.3-70b-versatile` (Groq provider)
  - `google/gemini-2.5-flash` (Google provider)
  - `openai/gpt-5.4` (OpenAI provider)
  - `baseline/zero-coeff` (deterministic synthetic baseline)
  - `baseline/small-coeff` (deterministic synthetic baseline)
  - `baseline/big-coeff` (deterministic synthetic baseline)
  - `baseline/constraint-saturating` (deterministic constraint-aware synthetic baseline)
- API keys must be set as environment variables (e.g., `GROQ_API_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`)
- Model configuration is handled via the `model_dependent_config` dictionary passed to `parameterize_dag()`.
- Note: Instructor covers most common structured-output and retry behavior, but for each provider/model you may still need code-level platform-specific configuration updates (e.g., response mode, reasoning flags, provider-specific config objects).

Example usage in code:
```python
instructor_model_name = "groq/llama-3.1-8b-instant"
client = instructor.from_provider(instructor_model_name)
model_dependent_config = {
    "temperature": 0.0,
}
```


### Install graphviz to the system

This software is called via our python codebase later.

```
sudo apt install graphviz
sudo apt install poppler-utils
```

### Venv setup and python package installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```

### Available DAGs

Please note that we have pre-specified dags as samples and also as reproducibility artifacts. However, note that our contribution is benchmarking framework itself. You can plug in any DAGs and LLMs (local or off-the-shelf APIs) as long as you follow the yaml structures and documentation. 

In our main experimental results, we have seven DAGs:

1. `chachexia1`
2. `expenditure`
3. `foodsecurity`
4. `algal2`
5. `lexical`
6. `liquefaction`
7. `stocks`

The above graph structures and effects are sourced from [BnRep repository](https://www.sciencedirect.com/science/article/pii/S0925231225001742) under MIT Liscence. We manually collected other semantic information, such as variable descriptions, and quantitative information, such as variable ranges. To know concrete input that framework uses for creating prompts, please check DAG yaml files. 

Representative YAML files:

- `dags/chachexia1/disease_informed_real_bounds_and_units.yaml`
- `dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml`
- `dags/foodsecurity/foodsecurity.yaml`
- `dags/algal2/algal2.yaml`
- `dags/lexical/lexical.yaml`
- `dags/liquefaction/liquefaction.yaml`
- `dags/stocks/stocks.yaml`

For ablation purposes, you can also find variant files such as `*_pe.yaml`, misspecification DAGs (e.g., `expenditure_sp_*.yaml`), and additional cachexia bound/unit variants in each folder. When you use those variant files, please make sure to use correct experimental flags, which we will explain next. 


### Run an experiment

The CLI requires a DAG YAML file, an LLM model, the number of loops to run, and a custom label for the experiment.

To see all available options and examples:
```bash
python main.py -h
```

Most Python scripts in this repository also provide CLI help (typically via `-h`/`--help`).

Basic run:
```bash
python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml -m groq/llama-3.1-8b-instant -l 5 --label exp1
```

With custom retry settings:
```bash
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml -m google/gemini-2.5-flash -l 10 --loop-retry-max 0 --label "exp baseline"
```

Baseline run example:
```bash
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml -m baseline/constraint-saturating -l 1 --loop-retry-max 0 --iterative-budget 1 --label "exp_sat_bl"
```

Available options:
- `dag_yaml`: Path to the DAG YAML file (required)
- `-m, --model`: LLM model to use (required)
- `-l, --loop`: Number of parameterization cycles to run (required)
- `--label`: Custom label for the experiment, used in log filenames (required). Spaces will be converted to underscores and converted to lowercase.
- `--loop-retry-max`: Maximum retries per loop on failure (default: 3)
- `--iterative-budget`: Max iterative feedback rounds per scenario (default: 5). Set to `0` to disable feedback entirely and accept the first LLM response without validation.

**Important Note on `--loop-retry-max`:**
This parameter controls retries for the **outer loop** (entire parameterization cycle) in case of catastrophic failures (API errors, crashes, etc.). It does **NOT** control the iterative feedback mechanism within each parameterization.

**Iterative feedback budget (`--iterative-budget`):**
Controls how many times the system will re-prompt the LLM with validation feedback per scenario before accepting a proposal. When set to `0`, the system skips validation entirely and accepts the first LLM response as-is. When set to `N > 0`, the system attempts up to `N` LLM calls per scenario, using validation feedback to refine the response. Default is `5`.

Logs are saved to `output/logs/` with filenames like `{timestamp}_{label}_loop_{N}.log`

### Baseline presets

This repository includes deterministic baseline presets that skip external LLM calls and still pass through the same parsing/validation/evaluation pipeline.

- `baseline/zero-coeff`: fixed coefficient `0.0` for intercept and all parent effects
- `baseline/small-coeff`: fixed coefficient `1e-4` for intercept and all parent effects
- `baseline/big-coeff`: fixed coefficient `1e4` for intercept and all parent effects
- `baseline/constraint-saturating`: equal-share initialization with global coefficient scaling and midpoint-centering to respect hard range constraints

Detailed baseline documentation:
- `docs/BASELINE_ZERO_COEFF_PRESET.md`
- `docs/BASELINE_CONSTRAINT_SATURATING_PRESET.md`
- `docs/constraint_saturating_baseline_note.tex` (paper-style mathematical note)

### How to handle experimental artifacts

Please refer to ARTIFACTS.md, where we are trying to summarize the artifacts in output folder. At this point, there are different types of files and some have inconsistent naming schemes. We try to make it more consistent. 

Further, some analysis script are more manual to specify experiment ids to peform bulk analysis opeartions. In the future, we will make it more smooth and user-friendly without juggling different scripts with various args. 

**Current workflow**:

1. Use `enumerate_unique_stat_files.py` to list up, sanity check and create commands for `quick_result.py` with experimental ids. 
2. Use quick_result.py commands with consistent labels (cf. `deprecated/bulk_quick_result.sh`)
3. Use `concatenate_stats.py` to combine per-label `*_aggregated_stats.csv` files into a single CSV for downstream analysis.
4. Optional: Use latex generation script, such as `deprecated/generate_latex_table.py`, to obtain latex table. Make sure to specify correct input csv paths generated by the step 3, and also output file names. 


**Some useful tooling (not our main contribution) for table generation**
Final table generation is currently split across `deprecated/generate_latex_table.py`, `deprecated/generate_latex_table_pp.py`, and `deprecated/generate_latex_table_misp.py`, with hardcoded assumptions and slightly different input conventions.

In the future, we plan to unity those visualization tooling, which is not the main part of the framework into a single unitfied tooling. 