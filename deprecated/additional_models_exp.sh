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
python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "cac_gpt54";
python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "exp_gpt54";
python main.py dags/foodsecurity/foodsecurity.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "foo_gpt54";
python main.py dags/algal2/algal2.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "alg_gpt54";
python main.py dags/lexical/lexical.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "lex_gpt54";
python main.py dags/liquefaction/liquefaction.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "liq_gpt54";
python main.py dags/stocks/stocks.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "sto_gpt54";

## TODO [later run] Cachexia1, unit tweak commands for GPT 5.4
python main.py dags/chachexia1/disease_informed_real_bounds_tweaked_units_nm.yaml -m openai/gpt-5.4 -l 25 --loop-retry-max 5 --label "nm_cac_gpt54";


## TODO [later run] - expenditure misspecification commands to be created
# expenditure_sp_owner_expenditure
python main.py dags/expenditure/expenditure_sp_owner_expenditure.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_owner_expenditure_gpt54_25_5"
# expenditure_sp_majorcards_dependents
python main.py dags/expenditure/expenditure_sp_majorcards_dependents.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_majorcards_dependents_gpt54_25_5"
# expenditure_sp_owner_share
python main.py dags/expenditure/expenditure_sp_owner_share.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_owner_share_gpt54_25_5"
# expenditure_sp_majorcards_selfemp
python main.py dags/expenditure/expenditure_sp_majorcards_selfemp.yaml --model openai/gpt-5.4 --loop 25 --loop-retry-max 7 --label "exp_sp_majorcards_selfemp_gpt54_25_5"