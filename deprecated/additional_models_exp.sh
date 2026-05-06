# scope of experiment: additional models for comparison


## DAG scopes
# cachexia1
# expenditure
# foodsecurity
# algal2
# lexical
# liquefaction
# stocks


## Models
# openai/gpt-5.4

## final command specification: --label naming scheme for main.py
# python main.py {dag yaml path} -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "{dag first three letters}_gpt54"


## DONE - TODO: create experimental commands, each main.py command, separated by ; and a new line
## Next, create labels and adjsut other commands
# [1] Complete
# python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "cac_gpt54";
python quick_result.py --bulk 20260321160644,20260321160717,20260321160751,20260321160819,20260321160844,20260321160912,20260321160942,20260321161025,20260321161054,20260321161119,20260321161144,20260321161215,20260321161310,20260321161336,20260321161403,20260321161434,20260321161509,20260321161537,20260321161625,20260321161654,20260321161720,20260321161809,20260321161852,20260321161933,20260321162016 --label "cac_gpt54_25_5";

# [2] Complete
# python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "exp_gpt54";
python quick_result.py --bulk 20260321162404,20260321162508,20260321162608,20260321162759,20260321162905,20260321163053,20260321163233,20260321163338,20260321163432,20260321163518,20260321163627,20260321163910,20260321164010,20260321164208,20260321164325,20260321164428,20260321164544,20260321164651,20260321164751,20260321164849,20260321164947,20260321165034,20260321165143,20260321165425,20260322113223 --label "exp_gpt54_25_5";

# [3] Complete
# python main.py dags/foodsecurity/foodsecurity.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "foo_gpt54";
python quick_result.py --bulk 20260321165617,20260321165643,20260321165724,20260321165755,20260321165820,20260321165849,20260321170013,20260321170036,20260321170058,20260321170125,20260321170140,20260321170155,20260321170250,20260321170319,20260321170336,20260321170421,20260321170513,20260321170541,20260321170601,20260321170704,20260322113336,20260322113352,20260322113406,20260322113420,20260322113437 --label "foo_gpt54_25_5";

# [4] Complete
# python main.py dags/algal2/algal2.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "alg_gpt54";
python quick_result.py --bulk 20260321170726,20260321170801,20260321170832,20260321170904,20260321170941,20260321171015,20260321171046,20260321171124,20260321171206,20260321171235,20260321171310,20260321171417,20260321171452,20260321171523,20260321171558,20260321171628,20260321171656,20260321171723,20260321171752,20260321171818,20260321171852,20260321171926,20260321171953,20260321172020,20260321172055 --label "alg_gpt54_25_5";

# [5] Complete
# python main.py dags/lexical/lexical.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "lex_gpt54";
python quick_result.py --bulk 20260321174028,20260322113456,20260322113534,20260322113614,20260322113658,20260322113744,20260322113824,20260322113906,20260322113956,20260322114038,20260322114124,20260322114204,20260322114249,20260322114335,20260322114412,20260322114448,20260322114542,20260322114630,20260322114713,20260322114747,20260322114829,20260322114858,20260322114938,20260322115020,20260322115058 --label "lex_gpt54_25_5";

# [6] Complete
# python main.py dags/liquefaction/liquefaction.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "liq_gpt54";
python quick_result.py --bulk 20260322115152,20260322115324,20260322115403,20260322115453,20260322115546,20260322115705,20260322115755,20260322115842,20260322115925,20260322120014,20260322120129,20260322120200,20260322120313,20260322120352,20260322120431,20260322120524,20260322120606,20260322120649,20260322120818,20260322120856,20260322120948,20260322121035,20260322121115,20260322121156,20260322121245 --label "liq_gpt54_25_5";

# [7] Complete
# python main.py dags/stocks/stocks.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "sto_gpt54";
python quick_result.py --bulk 20260321175605,20260321175706,20260321175803,20260321175904,20260321180002,20260321180105,20260321180203,20260321180259,20260321180356,20260321180459,20260321180553,20260321180652,20260321180749,20260321180851,20260321180948,20260321181047,20260321181144,20260321181245,20260321181344,20260321181446,20260321181545,20260321181645,20260321181751,20260321181845,20260321181948 --label "sto_gpt54_25_5";
### Unit tweak commands

## TODO [later run] Cachexia1, unit tweak commands for GPT 5.4
python main.py dags/chachexia1/disease_informed_real_bounds_tweaked_units_nm.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "nm_cac_gpt54";
python quick_result.py --bulk 20260322123014,20260322123041,20260322123103,20260322123130,20260322123200,20260322123228,20260322123253,20260322123320,20260322123346,20260322123413,20260322123442,20260322123507,20260322123534,20260322123559,20260322123630,20260322123656,20260322123723,20260322123751,20260322123816,20260322123843,20260322123907,20260322123936,20260322124010,20260322124044,20260322124112  --label "nm_cac_gpt54";

### Expenditure misspecification commands
## TODO [later run] - expenditure misspecification commands to be created
# expenditure_sp_owner_expenditure
# python main.py dags/expenditure/expenditure_sp_owner_expenditure.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_owner_expenditure_gpt54_25_5";
python quick_result.py --bulk 20260322124150,20260322124238,20260322124326,20260322124415,20260322124512,20260322124554,20260322124642,20260322124727,20260322124805,20260322124849,20260322124928,20260322125023,20260322125119,20260322125204,20260322125246,20260322125331,20260322125419,20260322125458,20260322125549,20260322125635,20260322125722,20260322125813,20260322125900,20260322125951,20260322130043  --label "exp_sp_owner_expenditure_gpt54_25_5";


# expenditure_sp_majorcards_dependents;
# python main.py dags/expenditure/expenditure_sp_majorcards_dependents.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_majorcards_dependents_gpt54_25_5";
python quick_result.py --bulk 20260322130137,20260322130226,20260322130312,20260322130352,20260322130433,20260322130520,20260322130611,20260322130657,20260322130743,20260322130828,20260322130921,20260322131011,20260322131102,20260322131143,20260322131224,20260322131315,20260322131408,20260322131456,20260322131546,20260322131640,20260322131730,20260322131822,20260322131911,20260322132006,20260322132052 --label "exp_sp_majorcards_dependents_gpt54_25_5";


# expenditure_sp_owner_share;
# python main.py dags/expenditure/expenditure_sp_owner_share.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_owner_share_gpt54_25_5";
python quick_result.py --bulk 20260322132143,20260322132230,20260322132324,20260322132417,20260322132512,20260322132609,20260322132655,20260322132745,20260322132837,20260322132926,20260322133012,20260322133059,20260322133153,20260322133237,20260322133325,20260322133408,20260322133500,20260322133544,20260322133637,20260322133723,20260322133816,20260322133902,20260322133946,20260322134034,20260322134126 --label "exp_sp_owner_share_gpt54_25_5";

# expenditure_sp_majorcards_selfemp;
# python main.py dags/expenditure/expenditure_sp_majorcards_selfemp.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_majorcards_selfemp_gpt54_25_5";
python quick_result.py --bulk 20260322134216,20260322134306,20260322134400,20260322134449,20260322134540,20260322134638,20260322134717,20260322134801,20260322134848,20260322134939,20260322135029,20260322135116,20260322135201,20260322135243,20260322135333,20260322135426,20260322135511,20260322135559,20260322135646,20260322135731,20260322135811,20260322135859,20260322135947,20260322140033,20260322140122 --label "exp_sp_majorcards_selfemp_gpt54_25_5";


# --start_id 20260322121245


(venv) [redacted]@penguin:~/pj/llm-scm$ ### Expenditure misspecification commands
## TODO [later run] - expenditure misspecification commands to be created
# expenditure_sp_owner_expenditure
# python main.py dags/expenditure/expenditure_sp_owner_expenditure.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_owner_expenditure_gpt54_25_5";
python quick_result.py --bulk 20260322124150,20260322124238,20260322124326,20260322124415,20260322124512,20260322124554,20260322124642,20260322124727,20260322124805,20260322124849,20260322124928,20260322125023,20260322125119,20260322125204,20260322125246,20260322125331,20260322125419,20260322125458,20260322125549,20260322125635,20260322125722,20260322125813,20260322125900,20260322125951,20260322130043  --label "exp_sp_owner_expenditure_gpt54_25_5";


# expenditure_sp_majorcards_dependents;
# python main.py dags/expenditure/expenditure_sp_majorcards_dependents.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_majorcards_dependents_gpt54_25_5";
python quick_result.py --bulk 20260322130137,20260322130226,20260322130312,20260322130352,20260322130433,20260322130520,20260322130611,20260322130657,20260322130743,20260322130828,20260322130921,20260322131011,20260322131102,20260322131143,20260322131224,20260322131315,20260322131408,20260322131456,20260322131546,20260322131640,20260322131730,20260322131822,20260322131911,20260322132006,20260322132052 --label "exp_sp_majorcards_dependents_gpt54_25_5";


# expenditure_sp_owner_share;
# python main.py dags/expenditure/expenditure_sp_owner_share.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_owner_share_gpt54_25_5";
python quick_result.py --bulk 20260322132143,20260322132230,20260322132324,20260322132417,20260322132512,20260322132609,20260322132655,20260322132745,20260322132837,20260322132926,20260322133012,20260322133059,20260322133153,20260322133237,20260322133325,20260322133408,20260322133500,20260322133544,20260322133637,20260322133723,20260322133816,20260322133902,20260322133946,20260322134034,20260322134126 --label "exp_sp_owner_share_gpt54_25_5";

# expenditure_sp_majorcards_selfemp;
# python main.py dags/expenditure/expenditure_sp_majorcards_selfemp.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_majorcards_selfemp_gpt54_25_5";
python quick_result.py --bulk 20260322134216,20260322134306,20260322134400,20260322134449,20260322134540,20260322134638,20260322134717,20260322134801,20260322134848,20260322134939,20260322135029,20260322135116,20260322135201,20260322135243,20260322135333,20260322135426,20260322135511,20260322135559,20260322135646,20260322135731,20260322135811,20260322135859,20260322135947,20260322140033,20260322140122 --label "exp_sp_majorcards_selfemp_gpt54_25_5";
Searching for experiment IDs in /home/[redacted]/pj/llm-scm/output...

Bulk mode: Processing 25 specified experiments
  ✓ 20260322124150 (1 files)
  ✓ 20260322124238 (1 files)
  ✓ 20260322124326 (1 files)
  ✓ 20260322124415 (1 files)
  ✓ 20260322124512 (1 files)
  ✓ 20260322124554 (1 files)
  ✓ 20260322124642 (1 files)
  ✓ 20260322124727 (1 files)
  ✓ 20260322124805 (1 files)
  ✓ 20260322124849 (1 files)
  ✓ 20260322124928 (1 files)
  ✓ 20260322125023 (1 files)
  ✓ 20260322125119 (1 files)
  ✓ 20260322125204 (1 files)
  ✓ 20260322125246 (1 files)
  ✓ 20260322125331 (1 files)
  ✓ 20260322125419 (1 files)
  ✓ 20260322125458 (1 files)
  ✓ 20260322125549 (1 files)
  ✓ 20260322125635 (1 files)
  ✓ 20260322125722 (1 files)
  ✓ 20260322125813 (1 files)
  ✓ 20260322125900 (1 files)
  ✓ 20260322125951 (1 files)
  ✓ 20260322130043 (1 files)

Total files to process: 25

--- Files to be combined (Ascending Order) ---
-> 20260322124150df_gt_llm_stat_df_1.csv
-> 20260322124238df_gt_llm_stat_df_1.csv
-> 20260322124326df_gt_llm_stat_df_1.csv
-> 20260322124415df_gt_llm_stat_df_1.csv
-> 20260322124512df_gt_llm_stat_df_1.csv
-> 20260322124554df_gt_llm_stat_df_1.csv
-> 20260322124642df_gt_llm_stat_df_1.csv
-> 20260322124727df_gt_llm_stat_df_1.csv
-> 20260322124805df_gt_llm_stat_df_1.csv
-> 20260322124849df_gt_llm_stat_df_1.csv
-> 20260322124928df_gt_llm_stat_df_1.csv
-> 20260322125023df_gt_llm_stat_df_1.csv
-> 20260322125119df_gt_llm_stat_df_1.csv
-> 20260322125204df_gt_llm_stat_df_1.csv
-> 20260322125246df_gt_llm_stat_df_1.csv
-> 20260322125331df_gt_llm_stat_df_1.csv
-> 20260322125419df_gt_llm_stat_df_1.csv
-> 20260322125458df_gt_llm_stat_df_1.csv
-> 20260322125549df_gt_llm_stat_df_1.csv
-> 20260322125635df_gt_llm_stat_df_1.csv
-> 20260322125722df_gt_llm_stat_df_1.csv
-> 20260322125813df_gt_llm_stat_df_1.csv
-> 20260322125900df_gt_llm_stat_df_1.csv
-> 20260322125951df_gt_llm_stat_df_1.csv
-> 20260322130043df_gt_llm_stat_df_1.csv

--- Combined DataFrame---
          l2_norm  l2_norm_normalized  l2_norm_normalized_without_single_parent_edges  relative_order_count  total_multi_parent_nodes                            source_file
0   177554.077542            0.967474                                        0.967474                     6                         8  20260322124150df_gt_llm_stat_df_1.csv
1   177542.812874            1.049327                                        1.049327                     6                         8  20260322124238df_gt_llm_stat_df_1.csv
2   177554.077452            0.899246                                        0.899246                     6                         8  20260322124326df_gt_llm_stat_df_1.csv
3    77551.000885            0.975984                                        0.975984                     6                         8  20260322124415df_gt_llm_stat_df_1.csv
4   177542.812877            0.902656                                        0.902656                     6                         8  20260322124512df_gt_llm_stat_df_1.csv
5    57556.052683            0.880739                                        0.880739                     6                         8  20260322124554df_gt_llm_stat_df_1.csv
6    77551.000660            0.932773                                        0.932773                     6                         8  20260322124642df_gt_llm_stat_df_1.csv
7   177542.812869            0.767779                                        0.767779                     6                         8  20260322124727df_gt_llm_stat_df_1.csv
8   177538.278697            0.859820                                        0.859820                     6                         8  20260322124805df_gt_llm_stat_df_1.csv
9   177554.077404            0.869645                                        0.869645                     6                         8  20260322124849df_gt_llm_stat_df_1.csv
10  177542.812883            0.979962                                        0.979962                     6                         8  20260322124928df_gt_llm_stat_df_1.csv
11    3540.290015            0.958350                                        0.958350                     6                         8  20260322125023df_gt_llm_stat_df_1.csv
12   15608.852141            0.756872                                        0.756872                     6                         8  20260322125119df_gt_llm_stat_df_1.csv
13   77551.001005            0.906470                                        0.906470                     6                         8  20260322125204df_gt_llm_stat_df_1.csv
14  177554.077460            0.914585                                        0.914585                     6                         8  20260322125246df_gt_llm_stat_df_1.csv
15   57556.052690            0.908717                                        0.908717                     6                         8  20260322125331df_gt_llm_stat_df_1.csv
16   77551.000847            0.859715                                        0.859715                     6                         8  20260322125419df_gt_llm_stat_df_1.csv
17  177554.077418            0.950557                                        0.950557                     6                         8  20260322125458df_gt_llm_stat_df_1.csv
18  177542.800482            0.870351                                        0.870351                     6                         8  20260322125549df_gt_llm_stat_df_1.csv
19  177554.077404            0.860434                                        0.860434                     6                         8  20260322125635df_gt_llm_stat_df_1.csv
20   15538.482001            0.932762                                        0.932762                     6                         8  20260322125722df_gt_llm_stat_df_1.csv
21  177538.278772            0.927840                                        0.927840                     6                         8  20260322125813df_gt_llm_stat_df_1.csv
22  177554.077345            0.921159                                        0.921159                     6                         8  20260322125900df_gt_llm_stat_df_1.csv
23  177538.278708            0.827449                                        0.827449                     6                         8  20260322125951df_gt_llm_stat_df_1.csv
24  177542.812919            0.873778                                        0.873778                     6                         8  20260322130043df_gt_llm_stat_df_1.csv

Successfully combined data. Total rows: 25

=======================================================
âœ¨ Aggregate Statistics for Combined Data
=======================================================
**Column: l2_norm**
  - Mean ($\mu$): 132030.1590
  - Std Dev ($\sigma$): 64467.9970
  - 95% CI: 132030.1590 ± 25271.4548
**Column: l2_norm_normalized**
  - Mean ($\mu$): 0.9022
  - Std Dev ($\sigma$): 0.0644
  - 95% CI: 0.9022 ± 0.0252
**Column: l2_norm_normalized_without_single_parent_edges**
  - Mean ($\mu$): 0.9022
  - Std Dev ($\sigma$): 0.0644
  - 95% CI: 0.9022 ± 0.0252
**Column: relative_order_count**
  - Mean ($\mu$): 6.0000
  - Std Dev ($\sigma$): 0.0000
  - 95% CI: 6.0000 ± 0.0000
  >> Aggregated M4 (relative_order_count) across runs: Mean = 6.0000, Std = 0.0000

Aggregated statistics saved to: output/20260322165209_exp_sp_owner_expenditure_gpt54_25_5_aggregated_stats.csv

Bar plot successfully saved to: output/20260322165209_exp_sp_owner_expenditure_gpt54_25_5_statistics_bar_plot.png

--- Generating Distribution Plots ---
  > Distribution plot for 'l2_norm' saved to: 20260322165209_exp_sp_owner_expenditure_gpt54_25_5_distribution_plot_l2_norm.png
  > Distribution plot for 'l2_norm_normalized' saved to: 20260322165209_exp_sp_owner_expenditure_gpt54_25_5_distribution_plot_l2_norm_normalized.png
  > Distribution plot for 'l2_norm_normalized_without_single_parent_edges' saved to: 20260322165209_exp_sp_owner_expenditure_gpt54_25_5_distribution_plot_l2_norm_normalized_without_single_parent_edges.png
  > Distribution plot for 'relative_order_count' saved to: 20260322165209_exp_sp_owner_expenditure_gpt54_25_5_distribution_plot_relative_order_count.png
Searching for experiment IDs in /home/[redacted]/pj/llm-scm/output...

Bulk mode: Processing 25 specified experiments
  ✓ 20260322130137 (1 files)
  ✓ 20260322130226 (1 files)
  ✓ 20260322130312 (1 files)
  ✓ 20260322130352 (1 files)
  ✓ 20260322130433 (1 files)
  ✓ 20260322130520 (1 files)
  ✓ 20260322130611 (1 files)
  ✓ 20260322130657 (1 files)
  ✓ 20260322130743 (1 files)
  ✓ 20260322130828 (1 files)
  ✓ 20260322130921 (1 files)
  ✓ 20260322131011 (1 files)
  ✓ 20260322131102 (1 files)
  ✓ 20260322131143 (1 files)
  ✓ 20260322131224 (1 files)
  ✓ 20260322131315 (1 files)
  ✓ 20260322131408 (1 files)
  ✓ 20260322131456 (1 files)
  ✓ 20260322131546 (1 files)
  ✓ 20260322131640 (1 files)
  ✓ 20260322131730 (1 files)
  ✓ 20260322131822 (1 files)
  ✓ 20260322131911 (1 files)
  ✓ 20260322132006 (1 files)
  ✓ 20260322132052 (1 files)

Total files to process: 25

--- Files to be combined (Ascending Order) ---
-> 20260322130137df_gt_llm_stat_df_1.csv
-> 20260322130226df_gt_llm_stat_df_1.csv
-> 20260322130312df_gt_llm_stat_df_1.csv
-> 20260322130352df_gt_llm_stat_df_1.csv
-> 20260322130433df_gt_llm_stat_df_1.csv
-> 20260322130520df_gt_llm_stat_df_1.csv
-> 20260322130611df_gt_llm_stat_df_1.csv
-> 20260322130657df_gt_llm_stat_df_1.csv
-> 20260322130743df_gt_llm_stat_df_1.csv
-> 20260322130828df_gt_llm_stat_df_1.csv
-> 20260322130921df_gt_llm_stat_df_1.csv
-> 20260322131011df_gt_llm_stat_df_1.csv
-> 20260322131102df_gt_llm_stat_df_1.csv
-> 20260322131143df_gt_llm_stat_df_1.csv
-> 20260322131224df_gt_llm_stat_df_1.csv
-> 20260322131315df_gt_llm_stat_df_1.csv
-> 20260322131408df_gt_llm_stat_df_1.csv
-> 20260322131456df_gt_llm_stat_df_1.csv
-> 20260322131546df_gt_llm_stat_df_1.csv
-> 20260322131640df_gt_llm_stat_df_1.csv
-> 20260322131730df_gt_llm_stat_df_1.csv
-> 20260322131822df_gt_llm_stat_df_1.csv
-> 20260322131911df_gt_llm_stat_df_1.csv
-> 20260322132006df_gt_llm_stat_df_1.csv
-> 20260322132052df_gt_llm_stat_df_1.csv

--- Combined DataFrame---
          l2_norm  l2_norm_normalized  l2_norm_normalized_without_single_parent_edges  relative_order_count  total_multi_parent_nodes                            source_file
0    57536.502990            0.976535                                        0.976535                     6                         8  20260322130137df_gt_llm_stat_df_1.csv
1   177536.476283            0.949525                                        0.949525                     6                         8  20260322130226df_gt_llm_stat_df_1.csv
2   177536.476257            0.938990                                        0.938990                     6                         8  20260322130312df_gt_llm_stat_df_1.csv
3    57536.503197            0.993443                                        0.993443                     6                         8  20260322130352df_gt_llm_stat_df_1.csv
4   177536.476307            0.907365                                        0.907365                     6                         8  20260322130433df_gt_llm_stat_df_1.csv
5    15536.610467            0.906636                                        0.906636                     6                         8  20260322130520df_gt_llm_stat_df_1.csv
6   177536.476203            1.008561                                        1.008561                     6                         8  20260322130611df_gt_llm_stat_df_1.csv
7    17536.469909            1.012020                                        1.012020                     6                         8  20260322130657df_gt_llm_stat_df_1.csv
8    17536.469228            0.963925                                        0.963925                     6                         8  20260322130743df_gt_llm_stat_df_1.csv
9    57536.503389            0.926175                                        0.926175                     6                         8  20260322130828df_gt_llm_stat_df_1.csv
10   17536.469148            0.983451                                        0.983451                     6                         8  20260322130921df_gt_llm_stat_df_1.csv
11  177536.476269            1.016092                                        1.016092                     6                         8  20260322131011df_gt_llm_stat_df_1.csv
12   57536.503306            0.926659                                        0.926659                     6                         8  20260322131102df_gt_llm_stat_df_1.csv
13   57536.503101            0.905797                                        0.905797                     6                         8  20260322131143df_gt_llm_stat_df_1.csv
14  197536.464004            1.164448                                        1.164448                     6                         8  20260322131224df_gt_llm_stat_df_1.csv
15   17536.477463            1.918648                                        1.918648                     6                         8  20260322131315df_gt_llm_stat_df_1.csv
16  177536.476319            0.963340                                        0.963340                     6                         8  20260322131408df_gt_llm_stat_df_1.csv
17    9536.505075            0.971076                                        0.971076                     6                         8  20260322131456df_gt_llm_stat_df_1.csv
18  177536.476306            0.998189                                        0.998189                     6                         8  20260322131546df_gt_llm_stat_df_1.csv
19  177536.476305            1.003167                                        1.003167                     6                         8  20260322131640df_gt_llm_stat_df_1.csv
20  147536.482766            1.000108                                        1.000108                     6                         8  20260322131730df_gt_llm_stat_df_1.csv
21  177536.463897            0.983993                                        0.983993                     6                         8  20260322131822df_gt_llm_stat_df_1.csv
22  177536.476310            1.094859                                        1.094859                     6                         8  20260322131911df_gt_llm_stat_df_1.csv
23  117536.472039            0.984442                                        0.984442                     6                         8  20260322132006df_gt_llm_stat_df_1.csv
24   57536.503114            1.005111                                        1.005111                     6                         8  20260322132052df_gt_llm_stat_df_1.csv

Successfully combined data. Total rows: 25

=======================================================
âœ¨ Aggregate Statistics for Combined Data
=======================================================
**Column: l2_norm**
  - Mean ($\mu$): 107136.4876
  - Std Dev ($\sigma$): 71955.9917
  - 95% CI: 107136.4876 ± 28206.7487
**Column: l2_norm_normalized**
  - Mean ($\mu$): 1.0201
  - Std Dev ($\sigma$): 0.1956
  - 95% CI: 1.0201 ± 0.0767
**Column: l2_norm_normalized_without_single_parent_edges**
  - Mean ($\mu$): 1.0201
  - Std Dev ($\sigma$): 0.1956
  - 95% CI: 1.0201 ± 0.0767
**Column: relative_order_count**
  - Mean ($\mu$): 6.0000
  - Std Dev ($\sigma$): 0.0000
  - 95% CI: 6.0000 ± 0.0000
  >> Aggregated M4 (relative_order_count) across runs: Mean = 6.0000, Std = 0.0000

Aggregated statistics saved to: output/20260322165214_exp_sp_majorcards_dependents_gpt54_25_5_aggregated_stats.csv

Bar plot successfully saved to: output/20260322165214_exp_sp_majorcards_dependents_gpt54_25_5_statistics_bar_plot.png

--- Generating Distribution Plots ---
  > Distribution plot for 'l2_norm' saved to: 20260322165214_exp_sp_majorcards_dependents_gpt54_25_5_distribution_plot_l2_norm.png
  > Distribution plot for 'l2_norm_normalized' saved to: 20260322165214_exp_sp_majorcards_dependents_gpt54_25_5_distribution_plot_l2_norm_normalized.png
  > Distribution plot for 'l2_norm_normalized_without_single_parent_edges' saved to: 20260322165214_exp_sp_majorcards_dependents_gpt54_25_5_distribution_plot_l2_norm_normalized_without_single_parent_edges.png
  > Distribution plot for 'relative_order_count' saved to: 20260322165214_exp_sp_majorcards_dependents_gpt54_25_5_distribution_plot_relative_order_count.png
Searching for experiment IDs in /home/[redacted]/pj/llm-scm/output...

Bulk mode: Processing 25 specified experiments
  ✓ 20260322132143 (1 files)
  ✓ 20260322132230 (1 files)
  ✓ 20260322132324 (1 files)
  ✓ 20260322132417 (1 files)
  ✓ 20260322132512 (1 files)
  ✓ 20260322132609 (1 files)
  ✓ 20260322132655 (1 files)
  ✓ 20260322132745 (1 files)
  ✓ 20260322132837 (1 files)
  ✓ 20260322132926 (1 files)
  ✓ 20260322133012 (1 files)
  ✓ 20260322133059 (1 files)
  ✓ 20260322133153 (1 files)
  ✓ 20260322133237 (1 files)
  ✓ 20260322133325 (1 files)
  ✓ 20260322133408 (1 files)
  ✓ 20260322133500 (1 files)
  ✓ 20260322133544 (1 files)
  ✓ 20260322133637 (1 files)
  ✓ 20260322133723 (1 files)
  ✓ 20260322133816 (1 files)
  ✓ 20260322133902 (1 files)
  ✓ 20260322133946 (1 files)
  ✓ 20260322134034 (1 files)
  ✓ 20260322134126 (1 files)

Total files to process: 25

--- Files to be combined (Ascending Order) ---
-> 20260322132143df_gt_llm_stat_df_1.csv
-> 20260322132230df_gt_llm_stat_df_1.csv
-> 20260322132324df_gt_llm_stat_df_1.csv
-> 20260322132417df_gt_llm_stat_df_1.csv
-> 20260322132512df_gt_llm_stat_df_1.csv
-> 20260322132609df_gt_llm_stat_df_1.csv
-> 20260322132655df_gt_llm_stat_df_1.csv
-> 20260322132745df_gt_llm_stat_df_1.csv
-> 20260322132837df_gt_llm_stat_df_1.csv
-> 20260322132926df_gt_llm_stat_df_1.csv
-> 20260322133012df_gt_llm_stat_df_1.csv
-> 20260322133059df_gt_llm_stat_df_1.csv
-> 20260322133153df_gt_llm_stat_df_1.csv
-> 20260322133237df_gt_llm_stat_df_1.csv
-> 20260322133325df_gt_llm_stat_df_1.csv
-> 20260322133408df_gt_llm_stat_df_1.csv
-> 20260322133500df_gt_llm_stat_df_1.csv
-> 20260322133544df_gt_llm_stat_df_1.csv
-> 20260322133637df_gt_llm_stat_df_1.csv
-> 20260322133723df_gt_llm_stat_df_1.csv
-> 20260322133816df_gt_llm_stat_df_1.csv
-> 20260322133902df_gt_llm_stat_df_1.csv
-> 20260322133946df_gt_llm_stat_df_1.csv
-> 20260322134034df_gt_llm_stat_df_1.csv
-> 20260322134126df_gt_llm_stat_df_1.csv

--- Combined DataFrame---
          l2_norm  l2_norm_normalized  l2_norm_normalized_without_single_parent_edges  relative_order_count  total_multi_parent_nodes                            source_file
0   117536.472062            0.963421                                        0.963421                     7                         8  20260322132143df_gt_llm_stat_df_1.csv
1    57536.503329            0.908647                                        0.908647                     6                         8  20260322132230df_gt_llm_stat_df_1.csv
2    87536.489687            0.968958                                        0.968958                     6                         8  20260322132324df_gt_llm_stat_df_1.csv
3    57536.503381            0.941002                                        0.941002                     7                         8  20260322132417df_gt_llm_stat_df_1.csv
4      466.959123            0.954498                                        0.954498                     6                         8  20260322132512df_gt_llm_stat_df_1.csv
5    15536.611407            0.914967                                        0.914967                     6                         8  20260322132609df_gt_llm_stat_df_1.csv
6     1537.121120            0.963897                                        0.963897                     6                         8  20260322132655df_gt_llm_stat_df_1.csv
7   177536.476181            0.954341                                        0.954341                     6                         8  20260322132745df_gt_llm_stat_df_1.csv
8    12536.509486            0.953844                                        0.953844                     6                         8  20260322132837df_gt_llm_stat_df_1.csv
9   177536.476312            1.018107                                        1.018107                     6                         8  20260322132926df_gt_llm_stat_df_1.csv
10  177536.463880            1.322227                                        1.322227                     6                         8  20260322133012df_gt_llm_stat_df_1.csv
11  177536.476243            0.933408                                        0.933408                     6                         8  20260322133059df_gt_llm_stat_df_1.csv
12    1537.126354            0.961537                                        0.961537                     6                         8  20260322133153df_gt_llm_stat_df_1.csv
13  117536.466836            0.892329                                        0.892329                     6                         8  20260322133237df_gt_llm_stat_df_1.csv
14  177536.476321            0.853800                                        0.853800                     6                         8  20260322133325df_gt_llm_stat_df_1.csv
15   97536.469069            1.028753                                        1.028753                     6                         8  20260322133408df_gt_llm_stat_df_1.csv
16   57536.503049            0.946546                                        0.946546                     6                         8  20260322133500df_gt_llm_stat_df_1.csv
17  177536.476266            0.968644                                        0.968644                     6                         8  20260322133544df_gt_llm_stat_df_1.csv
18   57536.502990            0.906330                                        0.906330                     7                         8  20260322133637df_gt_llm_stat_df_1.csv
19  177536.476313            2.092115                                        2.092115                     6                         8  20260322133723df_gt_llm_stat_df_1.csv
20  177536.476213            0.962985                                        0.962985                     6                         8  20260322133816df_gt_llm_stat_df_1.csv
21   17536.469110            0.958216                                        0.958216                     6                         8  20260322133902df_gt_llm_stat_df_1.csv
22     465.761967            1.073984                                        1.073984                     6                         8  20260322133946df_gt_llm_stat_df_1.csv
23    1537.119313            0.872202                                        0.872202                     6                         8  20260322134034df_gt_llm_stat_df_1.csv
24  177536.476309            0.937336                                        0.937336                     6                         8  20260322134126df_gt_llm_stat_df_1.csv

Successfully combined data. Total rows: 25

=======================================================
âœ¨ Aggregate Statistics for Combined Data
=======================================================
**Column: l2_norm**
  - Mean ($\mu$): 91970.9545
  - Std Dev ($\sigma$): 73871.3490
  - 95% CI: 91970.9545 ± 28957.5688
**Column: l2_norm_normalized**
  - Mean ($\mu$): 1.0101
  - Std Dev ($\sigma$): 0.2419
  - 95% CI: 1.0101 ± 0.0948
**Column: l2_norm_normalized_without_single_parent_edges**
  - Mean ($\mu$): 1.0101
  - Std Dev ($\sigma$): 0.2419
  - 95% CI: 1.0101 ± 0.0948
**Column: relative_order_count**
  - Mean ($\mu$): 6.1200
  - Std Dev ($\sigma$): 0.3317
  - 95% CI: 6.1200 ± 0.1300
  >> Aggregated M4 (relative_order_count) across runs: Mean = 6.1200, Std = 0.3317

Aggregated statistics saved to: output/20260322165218_exp_sp_owner_share_gpt54_25_5_aggregated_stats.csv

Bar plot successfully saved to: output/20260322165218_exp_sp_owner_share_gpt54_25_5_statistics_bar_plot.png

--- Generating Distribution Plots ---
  > Distribution plot for 'l2_norm' saved to: 20260322165218_exp_sp_owner_share_gpt54_25_5_distribution_plot_l2_norm.png
  > Distribution plot for 'l2_norm_normalized' saved to: 20260322165218_exp_sp_owner_share_gpt54_25_5_distribution_plot_l2_norm_normalized.png
  > Distribution plot for 'l2_norm_normalized_without_single_parent_edges' saved to: 20260322165218_exp_sp_owner_share_gpt54_25_5_distribution_plot_l2_norm_normalized_without_single_parent_edges.png
  > Distribution plot for 'relative_order_count' saved to: 20260322165218_exp_sp_owner_share_gpt54_25_5_distribution_plot_relative_order_count.png
Searching for experiment IDs in /home/[redacted]/pj/llm-scm/output...

Bulk mode: Processing 25 specified experiments
  ✓ 20260322134216 (1 files)
  ✓ 20260322134306 (1 files)
  ✓ 20260322134400 (1 files)
  ✓ 20260322134449 (1 files)
  ✓ 20260322134540 (1 files)
  ✓ 20260322134638 (1 files)
  ✓ 20260322134717 (1 files)
  ✓ 20260322134801 (1 files)
  ✓ 20260322134848 (1 files)
  ✓ 20260322134939 (1 files)
  ✓ 20260322135029 (1 files)
  ✓ 20260322135116 (1 files)
  ✓ 20260322135201 (1 files)
  ✓ 20260322135243 (1 files)
  ✓ 20260322135333 (1 files)
  ✓ 20260322135426 (1 files)
  ✓ 20260322135511 (1 files)
  ✓ 20260322135559 (1 files)
  ✓ 20260322135646 (1 files)
  ✓ 20260322135731 (1 files)
  ✓ 20260322135811 (1 files)
  ✓ 20260322135859 (1 files)
  ✓ 20260322135947 (1 files)
  ✓ 20260322140033 (1 files)
  ✓ 20260322140122 (1 files)

Total files to process: 25

--- Files to be combined (Ascending Order) ---
-> 20260322134216df_gt_llm_stat_df_1.csv
-> 20260322134306df_gt_llm_stat_df_1.csv
-> 20260322134400df_gt_llm_stat_df_1.csv
-> 20260322134449df_gt_llm_stat_df_1.csv
-> 20260322134540df_gt_llm_stat_df_1.csv
-> 20260322134638df_gt_llm_stat_df_1.csv
-> 20260322134717df_gt_llm_stat_df_1.csv
-> 20260322134801df_gt_llm_stat_df_1.csv
-> 20260322134848df_gt_llm_stat_df_1.csv
-> 20260322134939df_gt_llm_stat_df_1.csv
-> 20260322135029df_gt_llm_stat_df_1.csv
-> 20260322135116df_gt_llm_stat_df_1.csv
-> 20260322135201df_gt_llm_stat_df_1.csv
-> 20260322135243df_gt_llm_stat_df_1.csv
-> 20260322135333df_gt_llm_stat_df_1.csv
-> 20260322135426df_gt_llm_stat_df_1.csv
-> 20260322135511df_gt_llm_stat_df_1.csv
-> 20260322135559df_gt_llm_stat_df_1.csv
-> 20260322135646df_gt_llm_stat_df_1.csv
-> 20260322135731df_gt_llm_stat_df_1.csv
-> 20260322135811df_gt_llm_stat_df_1.csv
-> 20260322135859df_gt_llm_stat_df_1.csv
-> 20260322135947df_gt_llm_stat_df_1.csv
-> 20260322140033df_gt_llm_stat_df_1.csv
-> 20260322140122df_gt_llm_stat_df_1.csv

--- Combined DataFrame---
          l2_norm  l2_norm_normalized  l2_norm_normalized_without_single_parent_edges  relative_order_count  total_multi_parent_nodes                            source_file
0   177536.476215            1.685840                                        1.685840                     7                         9  20260322134216df_gt_llm_stat_df_1.csv
1   117536.472008            1.723939                                        1.723939                     7                         9  20260322134306df_gt_llm_stat_df_1.csv
2   177536.476327            1.679091                                        1.679091                     7                         9  20260322134400df_gt_llm_stat_df_1.csv
3   117536.466837            1.916279                                        1.916279                     7                         9  20260322134449df_gt_llm_stat_df_1.csv
4    57536.502962            1.632490                                        1.632490                     7                         9  20260322134540df_gt_llm_stat_df_1.csv
5    17536.469752            1.674377                                        1.674377                     7                         9  20260322134638df_gt_llm_stat_df_1.csv
6   117536.466810            1.657554                                        1.657554                     7                         9  20260322134717df_gt_llm_stat_df_1.csv
7    57536.503171            1.640500                                        1.640500                     7                         9  20260322134801df_gt_llm_stat_df_1.csv
8    57536.503130            1.672674                                        1.672674                     7                         9  20260322134848df_gt_llm_stat_df_1.csv
9   177536.476269            1.679381                                        1.679381                     7                         9  20260322134939df_gt_llm_stat_df_1.csv
10  177536.476272            1.635202                                        1.635202                     7                         9  20260322135029df_gt_llm_stat_df_1.csv
11    9536.505608            1.640891                                        1.640891                     7                         9  20260322135116df_gt_llm_stat_df_1.csv
12  177536.476337            1.833378                                        1.833378                     7                         9  20260322135201df_gt_llm_stat_df_1.csv
13  177536.476319            1.672568                                        1.672568                     7                         9  20260322135243df_gt_llm_stat_df_1.csv
14  177536.477027            1.662524                                        1.662524                     7                         9  20260322135333df_gt_llm_stat_df_1.csv
15  117536.466784            1.670445                                        1.670445                     7                         9  20260322135426df_gt_llm_stat_df_1.csv
16    9536.506144            1.619319                                        1.619319                     7                         9  20260322135511df_gt_llm_stat_df_1.csv
17   57536.513236            1.648277                                        1.648277                     7                         9  20260322135559df_gt_llm_stat_df_1.csv
18   77536.493038            1.661743                                        1.661743                     7                         9  20260322135646df_gt_llm_stat_df_1.csv
19  177536.477435            1.636057                                        1.636057                     7                         9  20260322135731df_gt_llm_stat_df_1.csv
20   17536.469971            2.476673                                        2.476673                     6                         9  20260322135811df_gt_llm_stat_df_1.csv
21  177536.476335            1.657301                                        1.657301                     7                         9  20260322135859df_gt_llm_stat_df_1.csv
22   57536.503229            2.366983                                        2.366983                     7                         9  20260322135947df_gt_llm_stat_df_1.csv
23    7536.535970            1.642332                                        1.642332                     7                         9  20260322140033df_gt_llm_stat_df_1.csv
24   17536.468700            1.670216                                        1.670216                     7                         9  20260322140122df_gt_llm_stat_df_1.csv

Successfully combined data. Total rows: 25

=======================================================
âœ¨ Aggregate Statistics for Combined Data
=======================================================
**Column: l2_norm**
  - Mean ($\mu$): 100496.4854
  - Std Dev ($\sigma$): 67752.2840
  - 95% CI: 100496.4854 ± 26558.8953
**Column: l2_norm_normalized**
  - Mean ($\mu$): 1.7382
  - Std Dev ($\sigma$): 0.2161
  - 95% CI: 1.7382 ± 0.0847
**Column: l2_norm_normalized_without_single_parent_edges**
  - Mean ($\mu$): 1.7382
  - Std Dev ($\sigma$): 0.2161
  - 95% CI: 1.7382 ± 0.0847
**Column: relative_order_count**
  - Mean ($\mu$): 6.9600
  - Std Dev ($\sigma$): 0.2000
  - 95% CI: 6.9600 ± 0.0784
  >> Aggregated M4 (relative_order_count) across runs: Mean = 6.9600, Std = 0.2000

Aggregated statistics saved to: output/20260322165222_exp_sp_majorcards_selfemp_gpt54_25_5_aggregated_stats.csv

Bar plot successfully saved to: output/20260322165222_exp_sp_majorcards_selfemp_gpt54_25_5_statistics_bar_plot.png

--- Generating Distribution Plots ---
  > Distribution plot for 'l2_norm' saved to: 20260322165222_exp_sp_majorcards_selfemp_gpt54_25_5_distribution_plot_l2_norm.png
  > Distribution plot for 'l2_norm_normalized' saved to: 20260322165222_exp_sp_majorcards_selfemp_gpt54_25_5_distribution_plot_l2_norm_normalized.png
  > Distribution plot for 'l2_norm_normalized_without_single_parent_edges' saved to: 20260322165222_exp_sp_majorcards_selfemp_gpt54_25_5_distribution_plot_l2_norm_normalized_without_single_parent_edges.png
  > Distribution plot for 'relative_order_count' saved to: 20260322165222_exp_sp_majorcards_selfemp_gpt54_25_5_distribution_plot_relative_order_count.png