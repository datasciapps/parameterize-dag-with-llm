# DAG YAML Conversion Guide

## Overview
The DAG system has been converted from Python module imports to YAML file definitions, making experiment setup easier and more flexible without requiring code changes.

## Files Created/Modified

### 1. **dag_yaml_loader.py** (NEW)
   - Loads DAG definitions from YAML files
   - Handles conversion of YAML data structures back to Python format
   - Converts:
     - List representations back to tuples for edges
     - String keys (format: "node1->node2") back to tuple keys
     - List representations back to sets for `all_nodes`

### 2. **verify_dag_conversion.py** (NEW)
   - Helper script to verify that Python and YAML DAG files match
   - Compares all key fields between Python `.py` and `.yaml` versions
   - Usage:
     ```bash
     python verify_dag_conversion.py
     ```
   - Output shows:
     - ✓ for matching DAGs
     - ✗ for mismatches or missing files
     - Detailed error messages

### 3. **main.py** (MODIFIED)
   - Now accepts an optional YAML file path as command-line argument
   - Falls back to default Python-defined DAG if no argument provided
   - Maintains backward compatibility

## Usage

### Method 1: Use Default Python DAG (Backward Compatible)
```bash
python main.py
```
This loads the default DAG: `expenditure_phenomena_informed_crafted_bounds`

### Method 2: Load DAG from YAML File
```bash
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml
```

### Method 3: Verify All DAG Conversions
```bash
python verify_dag_conversion.py
```

## YAML File Structure

Each YAML file represents a complete DAG definition:

```yaml
name: expenditure_phenomena_informed_crafted_bounds
all_nodes:
  - Card
  - Reports
  - Age
  - Income
  # ... more nodes

raw_edges:
  - [Card, Reports]        # [parent, child]
  - [Card, Share]
  # ... more edges

node_descriptions:
  Card: "Description of Card"
  Reports: "Description of Reports"
  # ... descriptions for all nodes

node_lower_bound:
  Card: 0
  Reports: 0
  # ... lower bounds

node_upper_bound:
  Card: 1
  Reports: 10
  # ... upper bounds

ground_truth_effect_sizes:
  Card->Reports: -1.52254735864156    # Format: "parent->child": value
  Active->Reports: 0.0524304077175797
  # ... more effect sizes

primary_domain_name: Finance
secondary_domain_name: Consumer Behavior
phenomenon_overview: "Description of the phenomenon..."
include_parent_relationships: false
```

## Key Differences from Python Files

| Aspect | Python | YAML |
|--------|--------|------|
| Tuples | `(a, b)` | `[a, b]` (list, converted back to tuple when loaded) |
| Sets | `{a, b, c}` | `[a, b, c]` (list, converted back to set when loaded) |
| Dict with tuple keys | `{(a, b): value}` | `a->b: value` (string key format) |
| Comments | `#` | `#` |
| Readability | Less readable | More readable |

## Data Type Conversions

When loading from YAML:

1. **raw_edges**: Lists → Tuples
   ```
   YAML: [[Card, Reports], [Card, Share]]
   Python: [("Card", "Reports"), ("Card", "Share")]
   ```

2. **all_nodes**: Lists → Sets
   ```
   YAML: [Card, Reports, Age]
   Python: {"Card", "Reports", "Age"}
   ```

3. **ground_truth_effect_sizes**: String keys → Tuple keys
   ```
   YAML: Card->Reports: -1.523
   Python: ("Card", "Reports"): -1.523
   ```

## Verification

To ensure all YAML files match their Python counterparts:

```bash
python verify_dag_conversion.py
```

Expected output:
```
✓ expenditure_phenomena_informed_crafted_bounds
✓ disease_informed_arbitrary_bounds
✓ disease_blind_arbitrary_bounds
... (and so on for all DAGs)

============================================================
Results: X match, 0 mismatch, 0 missing YAML
============================================================
All DAG conversions verified successfully!
```

## Benefits

1. **No Code Changes**: Experiments can be configured without writing Python code
2. **Human-Readable**: YAML is easy to read and edit
3. **Version Control Friendly**: Text-based format works well with git
4. **Flexible**: Easy to add new DAGs without modifying code
5. **Backward Compatible**: Existing Python imports still work

## Troubleshooting

### YAML File Not Found
```
FileNotFoundError: DAG YAML file not found: dags/example.yaml
```
Check that the file path is correct and the file exists.

### YAML Parse Error
```
yaml.YAMLError: ...
```
Check the YAML syntax. Common issues:
- Indentation must be consistent (use spaces, not tabs)
- Colons must be followed by spaces
- List items must start with `-`

### Conversion Mismatch
If `verify_dag_conversion.py` reports mismatches:
1. Re-run the conversion script: `python convert_dag_py_to_yaml.py`
2. Check the YAML file manually for issues
3. Verify the Python file has the expected structure

## Example: Adding a New DAG

1. Create a new YAML file in `dags/` directory
2. Define the DAG structure following the schema above
3. Run the verification script to ensure correctness:
   ```bash
   python verify_dag_conversion.py
   ```
4. Use it in main:
   ```bash
   python main.py dags/my_new_dag.yaml
   ```
