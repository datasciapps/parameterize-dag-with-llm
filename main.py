# -*- coding: utf-8 -*-

# from IPython.display import Image, display # Import Image and display
from dag_traversal_utility import GeneralDAGData
from llm_dag_parameterizer import parameterize_dag


from dags.chachexia1.disease_informed_arbitrary_bounds import cachexia1_disease_informed_arbitrary_bounds
from dags.chachexia1.disease_blind_arbitrary_bounds import cachexia1_disease_blind_arbitrary_bounds
from dags.chachexia1.disease_blind_real_bounds_and_units import cachexia1_disease_blind_real_bounds_and_units
from dags.chachexia1.disease_informed_real_bounds_and_units import cachexia1_disease_informed_real_bounds_and_units
from dags.chachexia1.disease_informed_real_bounds_tweaked_units_nm import cachexia1_disease_informed_real_bounds_tweaked_units_nm
from dags.chachexia1.disease_informed_real_bounds_tweaked_units_high_precision_nm import cachexia1_disease_informed_real_bounds_tweaked_units_high_precision_nm
"""
from dats.chacexia.disease_blind_arbitrary_bounds import
from dats.chacexia.disease_blind_real_bounds_and_units import
from dats.chacexia.disease_informed_real_bounds_and_units import
from dats.chacexia.disease_informed_real_bounds_tweaked_units_nm import
from dats.chacexia.disease_informed_real_bounds_tweaked_units_high_precision_nm import
"""

# import (
    # cachexia1_disease_informed_arbitrary_bounds,
# )
# import logging
# from google.colab import userdata
# from google.colab import drive # Drive is not used in this context
# os.environ["GEMINI_API_KEY"] = userdata.get("GOOGLE_API_KEY")



def main():
    """#### Main Loops for Cachexia Arbitrary Bounds

    ##### Cachexia 1 disease informed - arbitrary bounds
    """


    # parameterize_dag(cachexia1_exp1, include_hard_constraints=True)    
    # parameterize_dag(cachexia1_disease_informed_arbitrary_bounds, include_hard_constraints=True)
    current_dag_data: dict = cachexia1_disease_informed_arbitrary_bounds

    print(f"[Current DAG] {current_dag_data['name']}")
    
    parameterize_dag(
        GeneralDAGData(
            all_nodes = current_dag_data["all_nodes"],
            raw_edges = current_dag_data["raw_edges"],
            node_descriptions=current_dag_data["node_descriptions"],
            primary_domain_name=current_dag_data["primary_domain_name"],
            secondary_domain_name=current_dag_data["secondary_domain_name"],
            node_lower_bound=current_dag_data["node_lower_bound"],
            node_upper_bound=current_dag_data["node_upper_bound"],
            ground_truth_effect_sizes=current_dag_data["ground_truth_effect_sizes"],
            phenomenon_overview=current_dag_data["phenomenon_overview"],
        ),
        include_hard_constraints=True,
    )

    cachexia1_disease_informed_arbitrary_bounds
    cachexia1_disease_blind_arbitrary_bounds
    cachexia1_disease_blind_real_bounds_and_units
    cachexia1_disease_informed_real_bounds_and_units
    cachexia1_disease_informed_real_bounds_tweaked_units_nm
    cachexia1_disease_informed_real_bounds_tweaked_units_high_precision_nm

if __name__ == "__main__":
    main()