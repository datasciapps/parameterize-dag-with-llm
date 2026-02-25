"""
Module for loading DAG definitions from YAML files.
Converts YAML format back into the Python data structure compatible with the existing codebase.
"""

import yaml
from pathlib import Path


def load_dag_from_yaml(yaml_path: str) -> dict:
    """
    Load a DAG definition from a YAML file and return it as a dictionary.
    
    Args:
        yaml_path (str): Path to the YAML file
        
    Returns:
        dict: DAG definition dictionary compatible with GeneralDAGData
        
    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML is malformed
    """
    yaml_path = Path(yaml_path)
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")
    
    with open(yaml_path, 'r') as f:
        dag_data = yaml.safe_load(f)
    
    if dag_data is None:
        raise ValueError(f"YAML file is empty: {yaml_path}")
    
    # Convert lists back to tuples for raw_edges and ground_truth_effect_sizes keys
    if 'raw_edges' in dag_data and isinstance(dag_data['raw_edges'], list):
        dag_data['raw_edges'] = [tuple(edge) for edge in dag_data['raw_edges']]
    
    if 'ground_truth_effect_sizes' in dag_data and isinstance(dag_data['ground_truth_effect_sizes'], dict):
        # Convert string keys back to tuples
        converted_effect_sizes = {}
        for key, value in dag_data['ground_truth_effect_sizes'].items():
            # Key is stored as "node1->node2" string in YAML
            if isinstance(key, str) and '->' in key:
                node1, node2 = key.split('->')
                converted_effect_sizes[(node1, node2)] = value
            elif isinstance(key, list):
                # Fallback: if stored as list
                converted_effect_sizes[tuple(key)] = value
            else:
                converted_effect_sizes[key] = value
        dag_data['ground_truth_effect_sizes'] = converted_effect_sizes
    
    # Convert sets for all_nodes (stored as lists in YAML)
    if 'all_nodes' in dag_data and isinstance(dag_data['all_nodes'], list):
        dag_data['all_nodes'] = set(dag_data['all_nodes'])
    
    return dag_data


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dag_yaml_loader.py <path_to_yaml>")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    dag = load_dag_from_yaml(yaml_file)
    print(f"Loaded DAG: {dag['name']}")
    print(f"Nodes: {dag['all_nodes']}")
    print(f"Edges: {len(dag['raw_edges'])} edges")
