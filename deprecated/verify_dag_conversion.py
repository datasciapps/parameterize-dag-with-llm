"""
Helper script to verify that DAG Python files and their YAML counterparts contain the same data.
Checks for consistency between .py and .yaml versions of DAG definitions.
"""

import sys
from pathlib import Path
import yaml
import importlib.util
from typing import Tuple, List


def load_dag_from_python(py_path: str) -> dict:
    """Load a DAG definition from a Python file by importing it."""
    spec = importlib.util.spec_from_file_location("dag_module", py_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find the dictionary in the module (usually named with _informed_ or _blind_ pattern)
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, dict) and 'name' in attr and 'all_nodes' in attr:
            return attr
    
    raise ValueError(f"No DAG dictionary found in {py_path}")


def load_dag_from_yaml(yaml_path: str) -> dict:
    """Load a DAG definition from a YAML file."""
    with open(yaml_path, 'r') as f:
        dag_data = yaml.safe_load(f)
    
    if dag_data is None:
        raise ValueError(f"YAML file is empty: {yaml_path}")
    
    # Convert lists back to tuples for raw_edges
    if 'raw_edges' in dag_data and isinstance(dag_data['raw_edges'], list):
        dag_data['raw_edges'] = [tuple(edge) for edge in dag_data['raw_edges']]
    
    # Convert ground_truth_effect_sizes keys back to tuples
    if 'ground_truth_effect_sizes' in dag_data and isinstance(dag_data['ground_truth_effect_sizes'], dict):
        converted_effect_sizes = {}
        for key, value in dag_data['ground_truth_effect_sizes'].items():
            if isinstance(key, str) and '->' in key:
                node1, node2 = key.split('->')
                converted_effect_sizes[(node1, node2)] = value
            elif isinstance(key, list):
                converted_effect_sizes[tuple(key)] = value
            else:
                converted_effect_sizes[key] = value
        dag_data['ground_truth_effect_sizes'] = converted_effect_sizes
    
    # Convert all_nodes to set if it's a list
    if 'all_nodes' in dag_data and isinstance(dag_data['all_nodes'], list):
        dag_data['all_nodes'] = set(dag_data['all_nodes'])
    
    return dag_data


def compare_dags(py_dag: dict, yaml_dag: dict, py_path: str, yaml_path: str) -> Tuple[bool, List[str]]:
    """
    Compare two DAG definitions and return whether they match and any differences.
    
    Returns:
        Tuple[bool, List[str]]: (match, differences)
    """
    differences = []
    
    # Check key fields
    for key in ['name', 'all_nodes', 'raw_edges', 'node_descriptions', 'primary_domain_name', 
                'secondary_domain_name', 'node_lower_bound', 'node_upper_bound', 
                'ground_truth_effect_sizes', 'phenomenon_overview']:
        
        if key not in py_dag or key not in yaml_dag:
            if key not in py_dag and key not in yaml_dag:
                continue
            differences.append(f"  ✗ Key '{key}' missing in {'Python' if key not in py_dag else 'YAML'}")
            continue
        
        py_val = py_dag[key]
        yaml_val = yaml_dag[key]
        
        # Special handling for sets
        if isinstance(py_val, set) and isinstance(yaml_val, set):
            if py_val != yaml_val:
                differences.append(f"  ✗ {key}: Sets don't match")
        # Special handling for dicts with tuple keys
        elif isinstance(py_val, dict) and isinstance(yaml_val, dict):
            if py_val != yaml_val:
                differences.append(f"  ✗ {key}: Dictionaries don't match")
        # Special handling for lists of tuples
        elif isinstance(py_val, list) and isinstance(yaml_val, list):
            if py_val != yaml_val:
                differences.append(f"  ✗ {key}: Lists don't match")
        else:
            if py_val != yaml_val:
                differences.append(f"  ✗ {key}: Values don't match")
    
    return len(differences) == 0, differences


def main():
    """Find all DAG Python files and verify their YAML counterparts."""
    dag_dir = Path("dags")
    
    if not dag_dir.exists():
        print(f"Error: {dag_dir} directory not found")
        sys.exit(1)
    
    py_files = list(dag_dir.rglob("*.py"))
    
    if not py_files:
        print("No Python DAG files found")
        sys.exit(1)
    
    print(f"Found {len(py_files)} Python DAG files\n")
    
    matches = 0
    mismatches = 0
    missing = 0
    
    for py_file in sorted(py_files):
        yaml_file = py_file.with_suffix('.yaml')
        
        try:
            py_dag = load_dag_from_python(str(py_file))
            dag_name = py_dag.get('name', 'Unknown')
            
            if not yaml_file.exists():
                print(f"✗ {dag_name}")
                print(f"  YAML file missing: {yaml_file}")
                missing += 1
                continue
            
            yaml_dag = load_dag_from_yaml(str(yaml_file))
            
            match, differences = compare_dags(py_dag, yaml_dag, str(py_file), str(yaml_file))
            
            if match:
                print(f"✓ {dag_name}")
                matches += 1
            else:
                print(f"✗ {dag_name}")
                for diff in differences:
                    print(diff)
                mismatches += 1
        
        except Exception as e:
            print(f"✗ Error processing {py_file}: {e}")
            mismatches += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {matches} match, {mismatches} mismatch, {missing} missing YAML")
    print(f"{'='*60}")
    
    if mismatches > 0 or missing > 0:
        sys.exit(1)
    else:
        print("All DAG conversions verified successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
