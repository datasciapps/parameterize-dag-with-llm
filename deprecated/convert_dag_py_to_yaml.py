"""
Script to convert all Python DAG files to YAML format.
Handles tuples in raw_edges and ground_truth_effect_sizes.
"""

import os
import yaml
import importlib.util
from pathlib import Path


def load_dag_from_python_file(py_file_path):
    """Dynamically import a Python DAG file and extract its DAG object."""
    spec = importlib.util.spec_from_file_location("dag_module", py_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find all dictionaries that look like DAG definitions
    dags = {}
    for name, obj in module.__dict__.items():
        if isinstance(obj, dict) and "name" in obj and "raw_edges" in obj:
            dags[name] = obj
    
    return dags


def convert_dag_to_yaml_compatible(dag_dict):
    """
    Convert a DAG dictionary to a YAML-compatible format.
    - Sets are converted to sorted lists
    - Tuples in raw_edges are kept as lists
    - Tuples in ground_truth_effect_sizes keys are converted to "from->to" strings
    """
    converted = {}
    
    for key, value in dag_dict.items():
        if key == "all_nodes" and isinstance(value, set):
            # Convert set to sorted list for consistency
            converted[key] = sorted(list(value))
        elif key == "raw_edges" and isinstance(value, list):
            # Keep raw_edges as list of lists (tuples become lists in YAML)
            converted[key] = [list(edge) for edge in value]
        elif key == "ground_truth_effect_sizes" and isinstance(value, dict):
            # Convert tuple keys to "from->to" format
            converted[key] = {}
            for edge_tuple, effect_size in value.items():
                if isinstance(edge_tuple, tuple):
                    key_str = f"{edge_tuple[0]}->{edge_tuple[1]}"
                else:
                    key_str = str(edge_tuple)
                converted[key] = dict(sorted(converted[key].items()))
                converted[key][key_str] = effect_size
            # Sort by key for consistency
            converted[key] = dict(sorted(converted[key].items()))
        else:
            converted[key] = value
    
    return converted


def save_dag_as_yaml(dag_dict, output_path):
    """Save a DAG dictionary as a YAML file."""
    yaml_dict = convert_dag_to_yaml_compatible(dag_dict)
    
    with open(output_path, 'w') as f:
        yaml.dump(yaml_dict, f, default_flow_style=False, sort_keys=False)


def convert_all_dags_to_yaml(dags_directory):
    """
    Find all Python DAG files and convert them to YAML.
    """
    dags_dir = Path(dags_directory)
    converted_count = 0
    
    for py_file in dags_dir.rglob("*.py"):
        # Skip __pycache__ and __init__.py
        if "__pycache__" in str(py_file) or py_file.name == "__init__.py":
            continue
        
        print(f"\nProcessing: {py_file}")
        
        try:
            dag_dict = load_dag_from_python_file(py_file)
            
            for dag_name, dag_obj in dag_dict.items():
                # Create YAML file with same name as Python file
                yaml_file = py_file.with_suffix(".yaml")
                save_dag_as_yaml(dag_obj, yaml_file)
                print(f"✓ Converted to: {yaml_file}")
                converted_count += 1
        
        except Exception as e:
            print(f"✗ Error processing {py_file}: {e}")
    
    print(f"\n\nTotal converted: {converted_count} DAGs")


if __name__ == "__main__":
    dags_dir = os.path.expanduser("~/pj/llm-scm/dags")
    convert_all_dags_to_yaml(dags_dir)
