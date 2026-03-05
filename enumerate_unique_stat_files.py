#!/usr/bin/env python3
"""
enumerate_unique_stat_files.py

Lists all unique `gt_llm_stat_df` CSV files in the `output/` directory and extracts their experiment IDs (timestamps) from the filenames.

Usage:
    python enumerate_unique_stat_files.py

Output:
    Prints a table of experiment IDs and corresponding file names.
"""

from pathlib import Path
import re
import argparse

BASE_DIR = Path("./output")
SEARCH_PATTERN = "*gt_llm_stat_df*.csv"
LOG_DIR = BASE_DIR / "logs"
LOG_PATTERN = "*.log"


def main():
    parser = argparse.ArgumentParser(description="Enumerate unique gt_llm_stat_df files and experiment IDs.")
    parser.add_argument(
        "--grep",
        type=str,
        help="Substring to filter filenames (only keep files containing this substring)",
    )
    parser.add_argument(
        "--start_id",
        type=str,
        help="Start experiment ID (inclusive) for filtering by interval. Must be used with --end_id."
    )
    parser.add_argument(
        "--end_id",
        type=str,
        help="End experiment ID (inclusive) for filtering by interval. Must be used with --start_id."
    )
    parser.add_argument(
        "--dump-ids",
        action="store_true",
        help="If set, print a quick_result.py --bulk command with the filtered experiment IDs at the end."
    )
    args = parser.parse_args()

    # Validate start_id/end_id usage
    if args.end_id and not args.start_id:
        parser.error("--end_id must be specified together with --start_id.")

    if not BASE_DIR.is_dir():
        print(f"Error: Directory '{BASE_DIR}' not found.")
        return

    stat_files = [f for f in BASE_DIR.iterdir() if f.is_file() and f.match(SEARCH_PATTERN)]
    if args.grep:
        stat_files = [f for f in stat_files if args.grep in f.name]
    if not stat_files:
        print("No gt_llm_stat_df CSV files found.")
        return

    # Find all log files
    log_files = []
    if LOG_DIR.is_dir():
        log_files = [f for f in LOG_DIR.iterdir() if f.is_file() and f.match(LOG_PATTERN)]

    id_to_files = {}
    for file in stat_files:
        match = re.search(r"(\d{14})", file.name)
        if match:
            exp_id = match.group(1)
            id_to_files.setdefault(exp_id, []).append(file.name)
        else:
            print(f"Warning: Could not extract experiment ID from {file.name}")

    # Filter by start_id/end_id if specified
    if args.start_id:
        sorted_ids = sorted(id_to_files.keys())
        end_id = args.end_id if args.end_id else sorted_ids[-1]
        filtered_ids = [i for i in sorted_ids if args.start_id <= i <= end_id]
        id_to_files = {i: id_to_files[i] for i in filtered_ids}

    print("\nExperiment ID      | CSV Files                                 | Corresponding log file(s)         | # Successes")
    print("-------------------|-------------------------------------------|------------------------------------|-------------")
    for exp_id, files in sorted(id_to_files.items()):
        # Find log files that contain the exp_id (ignoring underscores)
        matching_logs = [log for log in log_files if exp_id in log.name.replace('_','')]
        log_metadata = []  # To store (log_name, dag_path, model_name)
        if not matching_logs:
            log_str = '(none)'
            success_count = ''
            success_lines = []
        else:
            if len(matching_logs) == 1:
                log_str = matching_logs[0].name
            else:
                log_str = f"{matching_logs[0].name}, ..., {matching_logs[-1].name}  [{len(matching_logs)} logs found]"
            # Count 'Complete successfully' lines in all matching logs
            success_count = 0
            success_lines = []
            for log in matching_logs:
                dag_path = ''
                model_name = ''
                try:
                    with open(log, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # Try to extract DAG path and model from the first 20 lines
                        for l in lines[:20]:
                            if '[Loading DAG from YAML]' in l:
                                dag_path = l.strip().split(']')[-1].strip()
                            if '[LLM Model]' in l:
                                model_name = l.strip().split(']')[-1].strip()
                        # Track the most recent stat file ID as we scan lines
                        last_stat_id = ''
                        stat_file_pattern = re.compile(r'(\d{14})df_gt_llm_stat')
                        for idx, line in enumerate(lines):
                            # Update last_stat_id if this line saves a stat file
                            stat_file_match = stat_file_pattern.search(line)
                            if stat_file_match:
                                last_stat_id = stat_file_match.group(1)
                            if 'Completed successfully' in line:
                                success_count += 1
                                # Use the most recent stat file ID seen above this line
                                stat_id = last_stat_id
                                success_lines.append((line.strip(), stat_id, dag_path, model_name, log.name))
                except Exception as e:
                    success_lines.append((f"[Error reading log: {log.name} - {e}]", '', '', '', log.name))
                log_metadata.append((log.name, dag_path, model_name))
        print(f"{exp_id} | {', '.join(files):<43} | {log_str:<34} | {success_count}")
        if success_lines:
            stat_ids_for_bulk = []
            for sline, stat_id, dag_path, model_name, logname in success_lines:
                extra = []
                if stat_id:
                    extra.append(f"stat_id: {stat_id}")
                    stat_ids_for_bulk.append(stat_id)
                if dag_path:
                    extra.append(f"DAG: {dag_path}")
                if model_name:
                    extra.append(f"Model: {model_name}")
                extra_str = ' | '.join(extra)
                print(f"    [SUCCESS] {sline}" + (f" [{extra_str}]" if extra_str else ""))
            # If there are exactly 25 stat_ids, print the quick_result.py --bulk command
            stat_ids_for_bulk = [sid for sid in stat_ids_for_bulk if sid]
            if len(stat_ids_for_bulk) == 25:
                print(f"\nTo aggregate these 25 experiments, run:")
                print(f"python quick_result.py --bulk {','.join(stat_ids_for_bulk)}\n")
            elif len(stat_ids_for_bulk) > 0:
                # Print warning in red if not 25, but still show the command
                print(f"\033[91m[WARNING] {len(stat_ids_for_bulk)} success indicators found (expected 25). Proceed with caution!\033[0m")
                print(f"\nTo aggregate these {len(stat_ids_for_bulk)} experiments, run:")
                print(f"python quick_result.py --bulk {','.join(stat_ids_for_bulk)}\n")
    print(f"\n{sum(len(files) for files in id_to_files.values())} stat files found after filtering.")

    # Dump command if requested
    if args.dump_ids:
        filtered_ids = list(id_to_files.keys())
        if filtered_ids:
            if len(filtered_ids) != 25:
                print(f"\n[WARNING] --dump-ids: {len(filtered_ids)} experiment IDs found (expected 25). Proceed with caution!")
            print("\nTo aggregate these experiments, run:")
            print(f"python quick_result.py --bulk {','.join(filtered_ids)}")
        else:
            print("\nNo experiment IDs to dump.")


if __name__ == "__main__":
    main()
