# YAML DAG System - Quick Start Guide

## 🎯 TL;DR

Your DAG system now supports YAML! Run experiments from YAML files instead of Python code.

### Quick Commands

```bash
# Use default DAG (backward compatible)
python main.py

# Load from a YAML file
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml

# Verify all YAML files match Python originals
python verify_dag_conversion.py
```

---

## 📁 What Was Added

| File | Purpose |
|------|---------|
| `dag_yaml_loader.py` | Loads YAML DAG files |
| `verify_dag_conversion.py` | Validates YAML ↔ Python consistency |
| `YAML_DAG_GUIDE.md` | Complete documentation |
| `YAML_DAG_EXAMPLES.py` | 10 usage examples |
| `dags/**/*.yaml` | 8 YAML DAG definitions |

---

## ✨ What You Can Do Now

### Before (Python Modules)
```bash
# Had to import Python modules
python main.py  # Always used the default DAG
```

### After (YAML Files)
```bash
# Can easily switch between DAGs via command line
python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml

# No code changes needed!
```

---

## 🚀 Getting Started

### 1. Try Loading a YAML DAG
```bash
python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml
```

### 2. Verify Everything Works
```bash
python verify_dag_conversion.py
```

Expected output:
```
✓ cachexia1_disease_blind_arbitrary_bounds
✓ cachexia1_disease_blind_real_bounds_and_units
... (7 total)

Results: 7 match, 0 mismatch, 0 missing YAML
All DAG conversions verified successfully!
```

### 3. Load YAML in Python Code
```python
from dag_yaml_loader import load_dag_from_yaml

dag = load_dag_from_yaml('dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml')
print(dag['name'])
print(f"Nodes: {dag['all_nodes']}")
```

---

## 📋 Available DAG Files

### Chachexia DAGs
- `dags/chachexia1/disease_informed_arbitrary_bounds.yaml`
- `dags/chachexia1/disease_blind_arbitrary_bounds.yaml`
- `dags/chachexia1/disease_blind_real_bounds_and_units.yaml`
- `dags/chachexia1/disease_informed_real_bounds_and_units.yaml`
- `dags/chachexia1/disease_informed_real_bounds_tweaked_units_nm.yaml`
- `dags/chachexia1/disease_informed_real_bounds_tweaked_units_high_precision_nm.yaml`

### Expenditure DAGs
- `dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml`
- `dags/expenditure/expenditure_spurious_edges_added.yaml`

---

## 🔄 Backward Compatibility

**All existing code still works!**

```bash
# This still works (uses default DAG)
python main.py

# This is now also possible (loads from YAML)
python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml
```

---

## 📚 Documentation Files

- **`YAML_DAG_GUIDE.md`** - Complete reference guide with schema specification
- **`IMPLEMENTATION_STATUS.md`** - Detailed implementation summary
- **`YAML_DAG_EXAMPLES.py`** - 10 real-world usage examples

---

## ❓ FAQ

**Q: Do I need to change anything in my existing code?**  
A: No! Everything is backward compatible. The Python imports still work.

**Q: How are tuples represented in YAML?**  
A: As lists `[item1, item2]` - they're automatically converted back to tuples when loaded.

**Q: Can I edit YAML files?**  
A: Yes! They're plain text and easy to edit with any text editor.

**Q: What if I want to create a new DAG?**  
A: Create a new YAML file in the `dags/` directory following the schema in `YAML_DAG_GUIDE.md`.

**Q: How do I verify my YAML file is correct?**  
A: Run `python verify_dag_conversion.py` to check all files.

---

## 💡 Key Benefits

✅ **Easy Configuration** - Edit YAML instead of Python code  
✅ **Human Readable** - Clear structure and format  
✅ **No Code Changes** - Existing code still works  
✅ **Version Control Friendly** - Works well with git  
✅ **Verified** - Helper script ensures data integrity  

---

## 🔍 Example Workflow

```bash
# 1. Check what DAGs are available
ls dags/**/*.yaml

# 2. Verify all are correct
python verify_dag_conversion.py

# 3. Run with a specific DAG
python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml

# 4. Or use the default
python main.py
```

---

## 📝 YAML Structure (Quick Reference)

```yaml
name: dag_name
all_nodes: [Node1, Node2, Node3]
raw_edges:
  - [Node1, Node2]
  - [Node2, Node3]
node_descriptions:
  Node1: "Description"
node_lower_bound: {Node1: 0}
node_upper_bound: {Node1: 100}
ground_truth_effect_sizes:
  Node1->Node2: 0.5
primary_domain_name: Domain
secondary_domain_name: Subdomain
phenomenon_overview: "Overview text"
include_parent_relationships: false
```

---

## 🆘 Troubleshooting

**FileNotFoundError: YAML file not found**
- Check the path is correct: `python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml`

**YAML parse error**
- Check indentation (use spaces, not tabs)
- Ensure colons are followed by spaces

**Data mismatch**
- Run `python verify_dag_conversion.py` to identify the issue

---

## 📞 Need Help?

- See `YAML_DAG_GUIDE.md` for detailed documentation
- Check `YAML_DAG_EXAMPLES.py` for code examples
- Review `IMPLEMENTATION_STATUS.md` for technical details

---

**Status**: ✅ Ready to Use  
**Compatibility**: 100% Backward Compatible  
**Verification**: 7/7 DAGs Verified ✓
