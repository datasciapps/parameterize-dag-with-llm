## LLM-SCM Parameterizer

**Author: Kanta Yamaoka, related to AI4Nof1 project**

An evaluation pipeline to see given a DAG, how well/poorly LLMs can parameterize SCM/Bayesian Network in linear and continuous domains. 

- The pipeline comes with multiple DAGs and their learned ground-truth paramters thanks to bnRep repository.  
- The LLM calling part is implemented via general instructor pagkage, so you can easily switch LLM to your favorite ones. Structured output, call-retry etc are handled by the instructor package.  
- The codebase is adapted to CLI environment, which will output all the artifacts (csv and pdf) into ./output directory. 

## Setup 

Developer's environment:
> Python 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] on linux

### Install graphviz to the system

This software is called via our python codebase later.

```
sudo apt install graphviz
```

### Venv setup and python package installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```


### Run an experiment

```
python main.py
```