ok created enumerate unique stat files to find trully successful ones along with the export quick_result commands

# Cleanup and Workflow Documentation

1. Write a document describing how logs and other output artifacts are created during pipeline execution.
2. Consider improvements for log collection, visualization, and analysis. # Please specify desired enhancements.

## From main.py Execution to Paper Write-up

In perfect world where program does not deplete timeout limit, but sometimes that can happen. Then the workflow could be more manual. 

1. Run `main.py` with the `--label` argument, using a consistent naming scheme for experiment tracking.
2. Retrieve the experiment IDs generated in the previous step.
3. Execute `quick_result.py --bulk {25 experimental ids} --label {your chosen label}` to aggregate results.
4. Use the printed output from `quick_result.py` or the files it generates for further analysis.

### Common Issues

- If you use consistent labeling in step 1, it is easy to run step 3. However, it is often easy to forget to retrieve experiment IDs. Automatic identification and grouping of experiment IDs by conditions would be helpful.
- For reference, `quick_result.py` uses the search pattern `*gt_llm_stat_df*.csv` to locate relevant files.

## Improvements

The script `enumerate_unique_stat_files.py` was created to identify truly successful experiment runs and to export ready-to-use `quick_result.py` commands.

On error, it helps to manually check the id and metadata (dag yaml path etc), so we added `enumerate_unique_stat_files_single.py`. This helps to rerun a few experiments and collect success experiment ids during debug. Also, in some edge cases the `enumerate_unique_stat.py` miss parent experiment ids and downstream child experiments. This may be because if the retry happens in the first run, then downstream ids are not easily found. For short-term fix, you can find such runs via this single enumeration script. 

## Remaining Manual Steps

After running the `quick_result.py` command, generating LaTeX files for tables may still require manual intervention if the `--label` argument was not remembered during quick result generation.

Already there is a hardcoded one, `generate_latex_table.py`. Maybe I will adjust that. 