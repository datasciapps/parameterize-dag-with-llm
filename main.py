# -*- coding: utf-8 -*-

# from IPython.display import Image, display # Import Image and display
from instructor import Instructor
import instructor
from dag_traversal_utility import GeneralDAGData
from dag_yaml_loader import load_dag_from_yaml
from llm_dag_parameterizer import parameterize_dag
from google.genai import types
import sys
from pathlib import Path

# Legacy Python imports (kept for backward compatibility)
from dags.expenditure.expenditure_phenomena_informed_crafted_bounds import (
    expenditure_phenomena_informed_crafted_bounds,
)

from dags.chachexia1.disease_informed_arbitrary_bounds import (
    cachexia1_disease_informed_arbitrary_bounds,
)
from dags.chachexia1.disease_blind_arbitrary_bounds import (
    cachexia1_disease_blind_arbitrary_bounds,
)
from dags.chachexia1.disease_blind_real_bounds_and_units import (
    cachexia1_disease_blind_real_bounds_and_units,
)
from dags.chachexia1.disease_informed_real_bounds_and_units import (
    cachexia1_disease_informed_real_bounds_and_units,
)
from dags.chachexia1.disease_informed_real_bounds_tweaked_units_nm import (
    cachexia1_disease_informed_real_bounds_tweaked_units_nm,
)
from dags.chachexia1.disease_informed_real_bounds_tweaked_units_high_precision_nm import (
    cachexia1_disease_informed_real_bounds_tweaked_units_high_precision_nm,
)

from dags.expenditure.expenditure_spurious_edges_added import (
    expenditure_sp_owner_expenditure,
    expenditure_sp_majorcards_dependents,
    expenditure_sp_owner_share,
    expenditure_sp_majorcards_selfemp,
)
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


def main(dag_yaml_path: str = None):
    """#### Main Loops for Cachexia Arbitrary Bounds

    ##### Cachexia 1 disease informed - arbitrary bounds
    
    Args:
        dag_yaml_path (str, optional): Path to a YAML DAG file. If not provided,
                                       defaults to the Python-defined DAG.
    """
    # [2] groq example
    instructor_model_name = "groq/llama-3.1-8b-instant"
    client: Instructor.AsyncInstructor = instructor.from_provider(instructor_model_name)
    model_dependent_config: dict = {
        "temperature": 0.0,
    }

    # [1] Gemini configuration example:
    # Initialize instructor client
    # instructor_model_name = "google/gemini-2.5-flash"
    # client: instructor.AsyncInstructor = instructor.from_provider(
    #     "google/gemini-2.5-flash",
    # )
    # model_dependent_config: dict = {
    #     "config": types.GenerateContentConfig(
    #         temperature=0,
    #         thinking_config=types.ThinkingConfig(
    #             thinking_budget=0,
    #         ),
    #         response_mime_type="application/json",
    #     )
    # }

    # Load DAG from YAML or use default Python-defined DAG
    if dag_yaml_path:
        if not Path(dag_yaml_path).exists():
            raise FileNotFoundError(f"DAG YAML file not found: {dag_yaml_path}")
        print(f"[Loading DAG from YAML] {dag_yaml_path}")
        current_dag_data = load_dag_from_yaml(dag_yaml_path)
    else:
        # Default: use Python-defined DAG
        current_dag_data = expenditure_phenomena_informed_crafted_bounds
    
    print(f"[Current DAG] {current_dag_data['name']}")

    parameterize_dag(
        GeneralDAGData(
            all_nodes=current_dag_data["all_nodes"],
            raw_edges=current_dag_data["raw_edges"],
            node_descriptions=current_dag_data["node_descriptions"],
            primary_domain_name=current_dag_data["primary_domain_name"],
            secondary_domain_name=current_dag_data["secondary_domain_name"],
            node_lower_bound=current_dag_data["node_lower_bound"],
            node_upper_bound=current_dag_data["node_upper_bound"],
            ground_truth_effect_sizes=current_dag_data["ground_truth_effect_sizes"],
            phenomenon_overview=current_dag_data["phenomenon_overview"],
            include_parent_relationships=current_dag_data.get("include_parent_relationships", False),
        ),
        include_hard_constraints=True,
        client=client,
        model_dependent_config=model_dependent_config,
        instructor_model_name=instructor_model_name,
    )

    cachexia1_disease_informed_arbitrary_bounds
    cachexia1_disease_blind_arbitrary_bounds
    cachexia1_disease_blind_real_bounds_and_units
    cachexia1_disease_informed_real_bounds_and_units
    cachexia1_disease_informed_real_bounds_tweaked_units_nm
    cachexia1_disease_informed_real_bounds_tweaked_units_high_precision_nm


if __name__ == "__main__":
    # Allow passing a YAML DAG file path as command-line argument
    if len(sys.argv) > 1:
        dag_yaml_file = sys.argv[1]
        main(dag_yaml_path=dag_yaml_file)
    else:
        main()
