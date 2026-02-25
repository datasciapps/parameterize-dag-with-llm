#!/usr/bin/env python3
"""
Check success status of parent relationships PE experiments and enumerate experiment IDs.
"""

import re
from pathlib import Path

# Labels for all PE experiments
PE_LABELS = [
    "foo_pe_l3_8b",
    "foo_pe_l3_70b",
    "foo_pe_gem25",
    "alg_pe_l3_8b",
    "alg_pe_l3_70b",
    "alg_pe_gem25",
    "lex_pe_l3_8b",
    "lex_pe_l3_70b",
    "lex_pe_gem25",
    "liq_pe_l3_8b",
    "liq_pe_l3_70b",
    "liq_pe_gem25",
    "sto_pe_l3_8b",
    "sto_pe_l3_70b",
    "sto_pe_gem25",
    "ex_pe_l3_8b",
    "ex_pe_l3_70b",
    "ex_pe_gem25",
    "cha_pe_l3_8b",
    "cha_pe_l3_70b",
    "cha_pe_gem25",
]

def get_experiment_ids(label):
    """Extract experiment IDs from logs for a given label.
    
    Looks for the pattern:
    [*****Experiment ID: {id} started.****
    ... (experiment runs)
    Completed successfully
    
    Returns all IDs found and counts how many have "Completed successfully" after them.
    """
    log_dir = Path("output/logs")
    
    # Find all log files matching this label
    pattern = f"*_{label}_*.log"
    log_files = list(log_dir.glob(pattern))
    
    if not log_files:
        return [], 0, 0
    
    ids_all = []
    ids_successful = []
    
    for log_file in log_files:
        with open(log_file, 'r') as f:
            content = f.read()
            
            # Split content into sections, each starting with an experiment ID
            # Pattern: [*****Experiment ID: 20260223114326 started.****
            sections = re.split(r'\[\*+Experiment ID: (\d{14}) started', content)
            
            # sections[0] is before first ID, then pairs of (id, content_after_id)
            for i in range(1, len(sections), 2):
                if i < len(sections):
                    exp_id = sections[i]
                    exp_content = sections[i+1] if i+1 < len(sections) else ""
                    
                    ids_all.append(exp_id)
                    
                    # Check if this specific experiment completed successfully
                    if "Completed successfully" in exp_content:
                        ids_successful.append(exp_id)
    
    # Return unique IDs (deduplicated) and success count
    unique_ids = sorted(set(ids_all))
    unique_successful = len(set(ids_successful))
    return unique_ids, len(unique_ids), unique_successful

def main():
    print("=" * 80)
    print("Parent Relationships PE Experiments - Success Check and ID Enumeration")
    print("=" * 80)
    
    results_summary = {}
    all_ids_by_label = {}
    
    for label in PE_LABELS:
        ids, count, success_count = get_experiment_ids(label)
        results_summary[label] = {
            'count': count,
            'success_count': success_count,
        }
        all_ids_by_label[label] = ids
        
        # Expected 25 runs per experiment
        expected = 25
        status = "✓ COMPLETE" if count == expected else "⚠ INCOMPLETE" if count > 0 else "✗ FAILED"
        
        # Show detailed status
        if count == expected:
            print(f"{label:<20} | IDs: {count:2d}/25 successful: {success_count:2d}/25 | {status}")
        elif count > 0:
            print(f"{label:<20} | IDs: {count:2d}/25 successful: {success_count:2d}/{count} | {status}")
        else:
            print(f"{label:<20} | IDs: {count:2d}/25 | {status}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_labels = len(PE_LABELS)
    complete_labels = sum(1 for s in results_summary.values() if s['count'] == 25)
    partial_labels = sum(1 for s in results_summary.values() if 0 < s['count'] < 25)
    total_ids = sum(s['count'] for s in results_summary.values())
    total_successful = sum(s['success_count'] for s in results_summary.values())
    
    print(f"Total configurations: {total_labels}")
    print(f"  ✓ Complete (25/25): {complete_labels}")
    print(f"  ⚠ Partial: {partial_labels}")
    print(f"  ✗ Failed (0/25): {total_labels - complete_labels - partial_labels}")
    print(f"Total experiment IDs extracted: {total_ids}")
    print(f"Total successful runs: {total_successful}")
    
    # Save IDs to file in quick_result.py bulk format
    output_file = Path("pe_experiment_ids.txt")
    with open(output_file, 'w') as f:
        for label in PE_LABELS:
            ids = all_ids_by_label[label]
            if ids:
                ids_str = ','.join(ids)
                f.write(f"python quick_result.py --bulk {ids_str} --label \"{label}\"\n")
            else:
                f.write(f"# {label}: NO EXPERIMENT IDS FOUND\n")
    
    print(f"\n✓ Saved bulk commands to: {output_file}")
    print("\nYou can now run:")
    print("  bash pe_experiment_ids.txt")
    print("or copy the commands from the file to execute them individually.")

if __name__ == "__main__":
    main()
