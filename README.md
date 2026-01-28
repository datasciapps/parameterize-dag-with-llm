## LLM-SCM Parameterizer

**Author: Kanta Yamaoka, related to AI4Nof1 project**

An evaluation pipeline to see given a DAG, how well/poorly LLMs can parameterize SCM/Bayesian Network in linear and continuous domains. 

- The pipeline comes with multiple DAGs and their learned ground-truth paramters thanks to bnRep repository.  
- The LLM calling part is implemented via general instructor pagkage, so you can easily switch LLM to your favorite ones. Structured output, call-retry etc are handled by the instructor package.  
- The codebase is adapted to CLI environment, which will output all the artifacts (csv and pdf) into ./output directory. 

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

Logs are saved to `output/logs/` with filenames like `{timestamp}_{label}_loop_{N}.log`

