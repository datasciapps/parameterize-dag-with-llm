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


def main(dag_yaml_path: str):
    """#### Main Loops for DAG Parameterization
    
    Args:
        dag_yaml_path (str): Path to a YAML DAG file (required).
    """
    if not Path(dag_yaml_path).exists():
        raise FileNotFoundError(f"DAG YAML file not found: {dag_yaml_path}")
    
    print(f"[Loading DAG from YAML] {dag_yaml_path}")
    current_dag_data = load_dag_from_yaml(dag_yaml_path)
    
    print(f"[Current DAG] {current_dag_data['name']}")

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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_dag_yaml_file>")
        print(f"Example: python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml")
        sys.exit(1)
    
    dag_yaml_file = sys.argv[1]
    main(dag_yaml_path=dag_yaml_file)
