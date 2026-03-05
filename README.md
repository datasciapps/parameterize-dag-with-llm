## LLM-SCM Parameterizer

An evaluation pipeline to see given a DAG, how well/poorly LLMs can parameterize SCM/Bayesian Network in linear and continuous domains. 

- The pipeline comes with multiple DAGs and their learned ground-truth parameters thanks to bnRep repository.  
- The LLM calling part is implemented via general instructor package, so you can easily switch LLM to your favorite ones. Structured output, call-retry etc are handled by the instructor package.  
- The codebase is adapted to CLI environment, which will output all the artifacts (csv and pdf) into ./output directory. 


## Call to action: Please help us improve the tooling to further investigate quantitative causal reasoning of LLMs! 

The tooling's improvement is ongoing, and I want your feedback. Feel free to report bugs, feature requests via this github repo. 

The tool is actively being developed along with our arxiv preprint.

[**Linear-LLM-SCM: Benchmarking LLMs for Coefficient Elicitation in Linear-Gaussian Causal Models**](https://arxiv.org/abs/2602.10282v1)

If you utilize our tooling for your future publications, please kindly cite us via the following bibtex:

```
@misc{yamaoka2026linearllmscmbenchmarkingllmscoefficient,
      title={Linear-LLM-SCM: Benchmarking LLMs for Coefficient Elicitation in Linear-Gaussian Causal Models}, 
      author={Kanta Yamaoka and Sumantrak Mukherjee and Thomas Gärtner and David Antony Selby and Stefan Konigorski and Eyke Hüllermeier and Viktor Bengs and Sebastian Josef Vollmer},
      year={2026},
      eprint={2602.10282},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2602.10282}, 
}
```

## Setup 

Developer's environment:
> Python 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] on linux

### LLM prerequisite

- Via the instructor package, you can use multiple LLM models from different providers.
- Supported models:
  - `groq/llama-3.1-8b-instant` (Groq provider)
  - `google/gemini-2.5-flash` (Google provider)
  - `google/gemini-2.0-flash` (Google provider)
- API keys must be set as environment variables (e.g., `GROQ_API_KEY`, `GOOGLE_API_KEY`)
- Model configuration is handled via the `model_dependent_config` dictionary passed to `parameterize_dag()`.

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


### Run an experiment

The CLI requires a DAG YAML file, an LLM model, the number of loops to run, and a custom label for the experiment.

Basic run:
```bash
python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml -m groq/llama-3.1-8b-instant -l 5 --label exp1
```

With custom retry settings:
```bash
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml -m google/gemini-2.5-flash -l 10 --loop-retry-max 0 --label "exp baseline"
```

Available options:
- `dag_yaml`: Path to the DAG YAML file (required)
- `-m, --model`: LLM model to use (required)
- `-l, --loop`: Number of parameterization cycles to run (required)
- `--label`: Custom label for the experiment, used in log filenames (required). Spaces will be converted to underscores and converted to lowercase.
- `--loop-retry-max`: Maximum retries per loop on failure (default: 3)

**Important Note on `--loop-retry-max`:**
This parameter controls retries for the **outer loop** (entire parameterization cycle) in case of catastrophic failures (API errors, crashes, etc.). It does **NOT** control the iterative feedback mechanism within each parameterization. The iterative feedback loop that validates and refines LLM responses has a separate, hardcoded limit of 5 iterations per scenario (`MAX_RETRIES = 5` in `llm_dag_parameterizer.py`). If validation fails after 5 feedback iterations, the system will use the last proposal even if invalid.

Logs are saved to `output/logs/` with filenames like `{timestamp}_{label}_loop_{N}.log`

### How to handle experimental artifacts

Please refer to ARTIFACTS.md, where we are trying to summarize the artifacts in output folder. At this point, there are different types of files and some have inconsistent naming schemes. We try to make it more consistent. 

Further, some analysis script are more manual to specify experiment ids to peform bulk analysis opeartions. In the future, we will make it more smooth and user-friendly without juggling different scripts with various args. 

**Current workflow** (which is suboptimal due to some manual --label or id specification):

1. Use `enumerate_unique_stat_files.py` to list up, sanity check and create commands for `quick_result.py` with experimental ids. 
2. Use quick_result.py commands with consistent labels (cf. `deprecated/bulk_quick_result.sh`)
3. Optional: Use latex generation script, such as `deprecated/generate_latex_table.py`, to obtain latex table. Make sure to specify correct input csv paths generated by the step 2, and also output file names. 

Currently admitted manually handling those experimental ids is a pain, and we plan to fix this issues soon. 