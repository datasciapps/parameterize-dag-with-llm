#!/usr/bin/env python
"""
Quick reference and examples for using YAML DAGs in the LLM-SCM project.
"""
from dag_yaml_loader import load_dag_from_yaml
import os
from dag_traversal_utility import GeneralDAGData
from pathlib import Path

# ============================================================================
# EXAMPLE 1: Load Default DAG (Backward Compatible)
# ============================================================================

# In main.py - load the default Python-defined DAG
# python main.py

# ============================================================================
# EXAMPLE 2: Load DAG from YAML File
# ============================================================================

# Command line:
# python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml

# In Python code:

dag = load_dag_from_yaml('dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml')
print(dag['name'])
print(f"Nodes: {dag['all_nodes']}")
print(f"Edges: {dag['raw_edges']}")

# ============================================================================
# EXAMPLE 3: Verify All DAG Conversions
# ============================================================================

# Command line:
# python verify_dag_conversion.py

# Expected output:
# ✓ cachexia1_disease_blind_arbitrary_bounds
# ✓ cachexia1_disease_blind_real_bounds_and_units
# ✓ cachexia1_disease_informed_arbitrary_bounds
# ✓ cachexia1_disease_informed_real_bounds_and_units
# ✓ cachexia1_disease_informed_real_bounds_tweaked_units_high_precision_nm
# ✓ cachexia1_disease_informed_real_bounds_tweaked_units_nm
# ✓ expenditure_phenomena_informed_crafted_bounds

# ============================================================================
# EXAMPLE 4: Using Loaded DAG with GeneralDAGData
# ============================================================================

# Load from YAML
yaml_dag = load_dag_from_yaml('dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml')

# Create GeneralDAGData object (same as before)
dag_data = GeneralDAGData(
    all_nodes=yaml_dag['all_nodes'],
    raw_edges=yaml_dag['raw_edges'],
    node_descriptions=yaml_dag['node_descriptions'],
    primary_domain_name=yaml_dag['primary_domain_name'],
    secondary_domain_name=yaml_dag['secondary_domain_name'],
    node_lower_bound=yaml_dag['node_lower_bound'],
    node_upper_bound=yaml_dag['node_upper_bound'],
    ground_truth_effect_sizes=yaml_dag['ground_truth_effect_sizes'],
    phenomenon_overview=yaml_dag['phenomenon_overview'],
    include_parent_relationships=yaml_dag.get('include_parent_relationships', False),
)

# Use with parameterize_dag (no changes needed to existing code)
# parameterize_dag(dag_data, ...)

# ============================================================================
# EXAMPLE 5: Data Type Conversions (What Happens Internally)
# ============================================================================

# YAML Input:
yaml_content = """
all_nodes:
  - Card
  - Reports
  - Age

raw_edges:
  - [Card, Reports]
  - [Card, Age]

ground_truth_effect_sizes:
  Card->Reports: -1.523
  Card->Age: 0.456
"""

# Python After Loading:
# all_nodes = {'Card', 'Reports', 'Age'}  # Set!
# raw_edges = [('Card', 'Reports'), ('Card', 'Age')]  # Tuples!
# ground_truth_effect_sizes = {
#     ('Card', 'Reports'): -1.523,  # Tuple keys!
#     ('Card', 'Age'): 0.456
# }

# ============================================================================
# EXAMPLE 6: Common File Paths
# ============================================================================

# Chachexia DAGs
# dags/chachexia1/disease_informed_arbitrary_bounds.yaml
# dags/chachexia1/disease_blind_arbitrary_bounds.yaml
# dags/chachexia1/disease_blind_real_bounds_and_units.yaml
# dags/chachexia1/disease_informed_real_bounds_and_units.yaml
# dags/chachexia1/disease_informed_real_bounds_tweaked_units_nm.yaml
# dags/chachexia1/disease_informed_real_bounds_tweaked_units_high_precision_nm.yaml

# Expenditure DAGs
# dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml
# dags/expenditure/expenditure_spurious_edges_added.yaml

# ============================================================================
# EXAMPLE 7: Checking if DAG Was Loaded from YAML vs Python
# ============================================================================

yaml_path = 'dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml'

if Path(yaml_path).exists():
    dag = load_dag_from_yaml(yaml_path)
    print(f"✓ Loaded from YAML: {dag['name']}")
else:
    print(f"✗ YAML file not found: {yaml_path}")
    # Fall back to Python import or handle error

# ============================================================================
# EXAMPLE 8: Creating a New YAML DAG File
# ============================================================================

# Create file: dags/my_domain/my_new_dag.yaml
# with content:

yaml_template = """
name: my_new_dag
all_nodes:
  - NodeA
  - NodeB
  - NodeC

raw_edges:
  - [NodeA, NodeB]
  - [NodeA, NodeC]
  - [NodeB, NodeC]

node_descriptions:
  NodeA: "Description for Node A"
  NodeB: "Description for Node B"
  NodeC: "Description for Node C"

node_lower_bound:
  NodeA: 0
  NodeB: 0
  NodeC: 0

node_upper_bound:
  NodeA: 100
  NodeB: 100
  NodeC: 100

ground_truth_effect_sizes:
  NodeA->NodeB: 0.5
  NodeA->NodeC: 0.3
  NodeB->NodeC: 0.2

primary_domain_name: MyDomain
secondary_domain_name: MySubdomain
phenomenon_overview: "Description of what this DAG represents"
include_parent_relationships: false
"""

# Then use it:
# python main.py dags/my_domain/my_new_dag.yaml

# ============================================================================
# EXAMPLE 9: Troubleshooting
# ============================================================================

# Problem: FileNotFoundError when loading YAML
# Solution: Check the path is correct relative to current working directory
print(os.getcwd())  # Check current directory
print(os.path.exists('dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml'))

# Problem: YAML syntax errors
# Solution: Check YAML formatting:
# - Use spaces, not tabs for indentation
# - Colons must be followed by space: key: value
# - Lists use dash: - item

# Problem: Data type mismatch after loading
# Solution: Use verify_dag_conversion.py to find issues:
# python verify_dag_conversion.py

# ============================================================================
# EXAMPLE 10: Using with Main Script
# ============================================================================

# Default behavior (no arguments):
# $ python main.py
# Loads: expenditure_phenomena_informed_crafted_bounds (Python default)

# Load specific YAML DAG:
# $ python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml
# Loads: disease_informed_arbitrary_bounds (from YAML)

# Load another variant:
# $ python main.py dags/chachexia1/disease_blind_real_bounds_and_units.yaml
# Loads: disease_blind_real_bounds_and_units (from YAML)

# ============================================================================
