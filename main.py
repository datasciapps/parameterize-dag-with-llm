# -*- coding: utf-8 -*-

# from IPython.display import Image, display # Import Image and display
from instructor import Instructor
import instructor
from dag_traversal_utility import GeneralDAGData
from dag_yaml_loader import load_dag_from_yaml
from llm_dag_parameterizer import parameterize_dag
from google.genai import types
import sys
import argparse
from pathlib import Path


# Model configurations
MODEL_CONFIGS = {
    "groq/llama-3.1-8b-instant": {
        "provider": "groq",
        "model_name": "groq/llama-3.1-8b-instant",
        "temperature": 0.0,
        "config": None,  # groq doesn't need special config
    },
    "google/gemini-2.5-flash": {
        "provider": "google",
        "model_name": "google/gemini-2.5-flash",
        "temperature": 0.0,
        "config": types.GenerateContentConfig(
            temperature=0,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            ),
            response_mime_type="application/json",
        ),
    },
}


def main(dag_yaml_path: str, model_name: str, num_loops: int):
    """#### Main Loops for DAG Parameterization
    
    Args:
        dag_yaml_path (str): Path to a YAML DAG file (required).
        model_name (str): Name of the LLM model to use (required).
                         Available models: groq/llama-3.1-8b-instant, 
                         google/gemini-2.5-flash, google/gemini-2.0-flash
        num_loops (int): Number of parameterization cycles to run (default: 1).
    """
    if not Path(dag_yaml_path).exists():
        raise FileNotFoundError(f"DAG YAML file not found: {dag_yaml_path}")
    
    if model_name not in MODEL_CONFIGS:
        available_models = ", ".join(MODEL_CONFIGS.keys())
        raise ValueError(f"Unknown model: {model_name}\nAvailable models: {available_models}")
    
    if num_loops < 1:
        raise ValueError(f"Number of loops must be >= 1, got {num_loops}")
    
    print(f"[Loading DAG from YAML] {dag_yaml_path}")
    current_dag_data = load_dag_from_yaml(dag_yaml_path)
    print(f"[Current DAG] {current_dag_data['name']}")
    
    print(f"[LLM Model] {model_name}")
    print(f"[Number of Loops] {num_loops}")
    
    model_config = MODEL_CONFIGS[model_name]
    
    # Initialize instructor client with selected model
    client: Instructor.AsyncInstructor = instructor.from_provider(model_name)
    
    # Prepare model-dependent config
    if model_config["config"] is not None:
        # For models with special config (like Google)
        model_dependent_config = {
            "config": model_config["config"]
        }
    else:
        # For models with simple config (like Groq)
        model_dependent_config = {
            "temperature": model_config["temperature"],
        }

    # Run parameterization in a loop
    for loop_num in range(1, num_loops + 1):
        print(f"\n{'='*80}")
        print(f"[Loop {loop_num}/{num_loops}]")
        print(f"{'='*80}\n")
        
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
            instructor_model_name=model_name,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run DAG parameterization with LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml --model groq/llama-3.1-8b-instant
  python main.py dags/chachexia1/disease_informed_arbitrary_bounds.yaml --model google/gemini-2.5-flash
  python main.py dags/expenditure/expenditure_phenomena_informed_crafted_bounds.yaml --model groq/llama-3.1-8b-instant --loop 5

Available models:
  - groq/llama-3.1-8b-instant
  - google/gemini-2.5-flash
  - google/gemini-2.0-flash
        """
    )
    
    parser.add_argument(
        "dag_yaml",
        help="Path to the DAG YAML file"
    )
    
    parser.add_argument(
        "--model",
        "-m",
        required=True,
        help="LLM model to use (e.g., groq/llama-3.1-8b-instant, google/gemini-2.5-flash)"
    )
    
    parser.add_argument(
        "--loop",
        "-l",
        type=int,
        required=True,
        help="Number of parameterization cycles to run (required)"
    )
    
    args = parser.parse_args()
    main(dag_yaml_path=args.dag_yaml, model_name=args.model, num_loops=args.loop)
