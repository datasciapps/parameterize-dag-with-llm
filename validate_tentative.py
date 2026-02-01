#!/usr/bin/env python3
"""
Validate the experiment ID mapping in tentative.txt against log files
"""
import os
import re
import glob

def extract_successful_experiments(label_pattern):
    """Extract successful experiment IDs for a given label pattern"""
    log_files = sorted(glob.glob(f"output/logs/*_{label_pattern}_*.log"))
    
    experiments = []
    for log_file in log_files:
        with open(log_file, 'r') as f:
            content = f.read()
            # Find all experiment IDs that were started
            started_ids = re.findall(r'\*\*\*\*\*Experiment ID: (\d+) started', content)
            # Check if loop completed successfully
            if 'Completed successfully' in content and started_ids:
                # Use the first ID (main one, not retries)
                experiments.append(started_ids[0])
    
    return experiments

def main():
    # Define the expected mappings from tentative.txt
    mappings = [
        ("foo_llama31_25_5", "Foodsecurity - Llama 3.1", 25),
        ("foo_llama33_25_5", "Foodsecurity - Llama 3.3", 25),
        ("foo_gemini25_25_5", "Foodsecurity - Gemini 2.5", 25),
        ("alg_llama31_25_5", "Algal2 - Llama 3.1", 25),
        ("alg_llama33_25_5", "Algal2 - Llama 3.3", 25),
        ("alg_gemini25_25_5", "Algal2 - Gemini 2.5", 25),
        ("lex_llama31_25_5", "Lexical - Llama 3.1", 25),
        ("lex_llama33_25_5", "Lexical - Llama 3.3", 25),
        ("lex_gemini25_25_5", "Lexical - Gemini 2.5", 7),  # INCOMPLETE
        ("liq_llama31_25_5", "Liquefaction - Llama 3.1", 25),
        ("liq_llama33_25_5", "Liquefaction - Llama 3.3", 25),
        ("liq_gemini25_25_5", "Liquefaction - Gemini 2.5", 25),
        ("sto_llama31_25_5", "Stocks - Llama 3.1", 25),
        ("sto_llama33_25_5", "Stocks - Llama 3.3", 25),
        ("sto_gemini25_25_5", "Stocks - Gemini 2.5", 25),
    ]
    
    print("=" * 80)
    print("VALIDATION REPORT: Experiment IDs from Log Files")
    print("=" * 80)
    print()
    
    all_experiments = []
    
    for label, name, expected_count in mappings:
        experiments = extract_successful_experiments(label)
        actual_count = len(experiments)
        
        status = "✓ CORRECT" if actual_count == expected_count else "✗ MISMATCH"
        
        print(f"{name} ({label})")
        print(f"  Expected: {expected_count} iterations")
        print(f"  Actual:   {actual_count} iterations {status}")
        
        if experiments:
            print(f"  IDs: {experiments[0]} - {experiments[-1]}")
            all_experiments.extend([(exp_id, name) for exp_id in experiments])
        else:
            print(f"  IDs: None found")
        print()
    
    print("=" * 80)
    print("ALL EXPERIMENT IDs IN CHRONOLOGICAL ORDER")
    print("=" * 80)
    print()
    
    for i, (exp_id, name) in enumerate(all_experiments, start=1):
        print(f"  [{i+226}] {exp_id} - {name}")

if __name__ == "__main__":
    main()
