from pydantic import BaseModel, ConfigDict
import pandas as pd
import instructor
import time
import json

from src.validator_utlity import (
    compute_predicted_target_range,
    compute_range_midpoint,
)


# Pydantic model for LLM response
class LLMParamResponse(BaseModel):
    plausibility: str
    proposed_lin_str_eq: str


class LLMParamResponseNoReasoning(BaseModel):
    proposed_lin_str_eq: str


def _format_coefficient(value: float) -> str:
    return format(float(value), ".12g")


def _build_synthetic_equation(
    target_variable_name: str,
    intercept: float,
    parent_coefficients: dict[str, float],
    parent_variables: list[str],
) -> str:
    intercept_term = f"{_format_coefficient(intercept)}*1"
    parent_terms = [
        f"{_format_coefficient(parent_coefficients[parent])}*{parent}"
        for parent in parent_variables
    ]
    equation_terms = " + ".join([intercept_term] + parent_terms)
    return f"{target_variable_name} = {equation_terms} + E_{target_variable_name}"


def _generate_fixed_coefficient_baseline(
    scenario_to_process: dict,
    baseline_coefficient: float,
) -> tuple[str, dict[str, float]]:
    parent_variables = scenario_to_process["direct_parent_variables"]
    target_variable_name = scenario_to_process["target_variable_name"]
    parent_coefficients = {
        parent_variable: baseline_coefficient for parent_variable in parent_variables
    }
    proposed_lin_str_eq = _build_synthetic_equation(
        target_variable_name=target_variable_name,
        intercept=baseline_coefficient,
        parent_coefficients=parent_coefficients,
        parent_variables=parent_variables,
    )
    return proposed_lin_str_eq, parent_coefficients


def _generate_constraint_saturating_baseline(
    scenario_to_process: dict,
) -> tuple[str, dict[str, float], dict[str, float]]:
    target_variable_name = scenario_to_process["target_variable_name"]
    parent_variables = scenario_to_process["direct_parent_variables"]
    node_lower_bounds = scenario_to_process["node_lower_bounds"]
    node_upper_bounds = scenario_to_process["node_upper_bounds"]

    if not parent_variables:
        raise ValueError(
            f"Constraint-saturating baseline requires at least one parent for '{target_variable_name}'."
        )

    target_lower_bound = node_lower_bounds.get(target_variable_name)
    target_upper_bound = node_upper_bounds.get(target_variable_name)
    if target_lower_bound is None or target_upper_bound is None:
        raise ValueError(
            f"Constraint-saturating baseline requires hard bounds for target '{target_variable_name}'."
        )
    if target_upper_bound < target_lower_bound:
        raise ValueError(
            f"Invalid bounds for target '{target_variable_name}': [{target_lower_bound}, {target_upper_bound}]"
        )

    equal_share_coefficient = 1.0 / len(parent_variables)
    unscaled_parent_coefficients = {
        parent_variable: equal_share_coefficient for parent_variable in parent_variables
    }
    unscaled_range = compute_predicted_target_range(
        intercept=0.0,
        parent_coefficients=unscaled_parent_coefficients,
        direct_parent_variables=parent_variables,
        node_lower_bounds=node_lower_bounds,
        node_upper_bounds=node_upper_bounds,
    )

    induced_width = (
        unscaled_range["max_predicted_target"]
        - unscaled_range["min_predicted_target"]
    )
    target_width = target_upper_bound - target_lower_bound

    if induced_width <= 0:
        scale_factor = 1.0
        scaled_parent_coefficients = {
            parent_variable: 0.0 for parent_variable in parent_variables
        }
    else:
        scale_factor = min(1.0, target_width / induced_width)
        scaled_parent_coefficients = {
            parent_variable: coefficient * scale_factor
            for parent_variable, coefficient in unscaled_parent_coefficients.items()
        }

    scaled_range = compute_predicted_target_range(
        intercept=0.0,
        parent_coefficients=scaled_parent_coefficients,
        direct_parent_variables=parent_variables,
        node_lower_bounds=node_lower_bounds,
        node_upper_bounds=node_upper_bounds,
    )
    contribution_midpoint = compute_range_midpoint(
        scaled_range["min_predicted_target"],
        scaled_range["max_predicted_target"],
    )
    target_midpoint = compute_range_midpoint(target_lower_bound, target_upper_bound)
    intercept = target_midpoint - contribution_midpoint

    final_range = compute_predicted_target_range(
        intercept=intercept,
        parent_coefficients=scaled_parent_coefficients,
        direct_parent_variables=parent_variables,
        node_lower_bounds=node_lower_bounds,
        node_upper_bounds=node_upper_bounds,
    )
    proposed_lin_str_eq = _build_synthetic_equation(
        target_variable_name=target_variable_name,
        intercept=intercept,
        parent_coefficients=scaled_parent_coefficients,
        parent_variables=parent_variables,
    )

    baseline_metadata = {
        "scale_factor": scale_factor,
        "target_lower_bound": target_lower_bound,
        "target_upper_bound": target_upper_bound,
        "predicted_lower_bound": final_range["min_predicted_target"],
        "predicted_upper_bound": final_range["max_predicted_target"],
    }
    return proposed_lin_str_eq, scaled_parent_coefficients, baseline_metadata


def run_llm_elicitation(
    client: instructor.AsyncInstructor,
    elicitation_prompt: str,
    scenario_to_process: dict,
    model_dependent_config: dict,  # This is unpacked into client.create as arguments.
    wait_sec_per_chat=0.2,
    debug_print=True,
    num_responses_per_prompt: int = 1,
) -> pd.DataFrame:
    """Runs the LLM elicitation process for a single prompt multiple times to collect varied responses.

    If model_dependent_config contains 'is_fake_baseline': True, returns a synthetic
    strategy-based baseline response. This is used for presets such as
    `baseline/zero-coeff`, `baseline/small-coeff`, `baseline/big-coeff`, and
    `baseline/constraint-saturating`.
    """
    assert len(elicitation_prompt) > 0
    assert scenario_to_process is not None

    if num_responses_per_prompt > 1:
        raise NotImplementedError("Currently only single response is supported.")

    # Check if this is a fake baseline mode
    is_fake_baseline = model_dependent_config.get("is_fake_baseline", False)
    baseline_strategy = model_dependent_config.get(
        "baseline_strategy", "fixed-coefficient"
    )
    disable_reasoning_tokens = model_dependent_config.get(
        "disable_reasoning_tokens", False
    )
    
    response_history: list[dict] = []
    
    # Handle fake baseline mode: synthesize response with a fixed coefficient value
    if is_fake_baseline:
        baseline_coefficient = model_dependent_config.get("baseline_coefficient", 0.0)
        baseline_label = model_dependent_config.get("baseline_label", "Baseline")

        if debug_print:
            print(f"[BASELINE MODE] {baseline_label} baseline activated.")
            print(f"[BASELINE MODE] Target variable: {scenario_to_process['target_variable_name']}")

        if baseline_strategy == "constraint-saturating":
            proposed_lin_str_eq, _, baseline_metadata = (
                _generate_constraint_saturating_baseline(scenario_to_process)
            )
            baseline_summary = (
                "Baseline: Equal-share coefficients globally scaled to fit hard constraints "
                f"(scale={baseline_metadata['scale_factor']:.4f}, "
                f"predicted range=[{baseline_metadata['predicted_lower_bound']:.4f}, "
                f"{baseline_metadata['predicted_upper_bound']:.4f}], "
                f"target range=[{baseline_metadata['target_lower_bound']:.4f}, "
                f"{baseline_metadata['target_upper_bound']:.4f}])."
            )
        else:
            proposed_lin_str_eq, _ = _generate_fixed_coefficient_baseline(
                scenario_to_process=scenario_to_process,
                baseline_coefficient=baseline_coefficient,
            )
            baseline_summary = (
                f"Baseline: All coefficients fixed to {baseline_coefficient} for preset testing."
            )
        
        if debug_print:
            print("[BASELINE MODE] Synthetic equation:")
            print(proposed_lin_str_eq)
        
        if disable_reasoning_tokens:
            response_json = {
                "proposed_lin_str_eq": proposed_lin_str_eq,
            }
        else:
            response_json = {
                "plausibility": (
                    baseline_summary
                ),
                "proposed_lin_str_eq": proposed_lin_str_eq,
            }
        response_history.append(response_json)
        
        if debug_print:
            print("*****MODEL (BASELINE SYNTHETIC RESPONSE)*****")
            print(json.dumps(response_json, indent=2))
        
        df = pd.DataFrame(response_history)
        return df
    
    # Real LLM mode (not baseline)
    provider_call_config = {
        key: value
        for key, value in model_dependent_config.items()
        if key
        not in {
            "disable_reasoning_tokens",
            "is_fake_baseline",
            "baseline_strategy",
            "baseline_coefficient",
            "baseline_label",
        }
    }

    for i in range(num_responses_per_prompt):
        # raise NotImplementedError("_create_llm_dynamic_validator_class is not implemented")
        if wait_sec_per_chat != 0:
            time.sleep(
                wait_sec_per_chat
            )  # To avoid rate limit, wait for each chat API call
        if debug_print:
            print("*****ELICITATION PROMPT*****")
            print(elicitation_prompt)

        try:
            # Use instructor to create the response, leveraging the Pydantic model
            response_model_class = (
                LLMParamResponseNoReasoning
                if disable_reasoning_tokens
                else LLMParamResponse
            )
            response_obj = client.create(
                response_model=response_model_class,
                messages=[
                    {
                        "role": "user",
                        "content": elicitation_prompt,
                    }
                ],
                **provider_call_config,
            )
            # Convert the Pydantic model instance to a dictionary for history storage
            response_json = response_obj.model_dump()
            proposed_lin_str_eq: str = response_json.get("proposed_lin_str_eq", "")
            print(
                "[Run LLM Elicitation] Proposed Linear String Equation (early validation):"
            )
            print(proposed_lin_str_eq)
            scenario_parents = scenario_to_process["direct_parent_variables"]
            # scenario_parents.append("0") # For intercept (edge case)

            # 2. Replace assert with if/raise ValueError
            for parent_var_name in scenario_parents:
                if parent_var_name not in proposed_lin_str_eq:
                    raise ValueError(
                        f"Missing coefficient for parent variable '{parent_var_name}' in LLM response. "
                        f"Required: beta_{parent_var_name} but not found in {proposed_lin_str_eq}"
                    )

        except Exception as e:
            print(
                f"Error during LLM elicitation with instructor (iteration {i + 1}): {e}"
            )
            # Appending an error dict to maintain DataFrame structure and signal the issue
            if disable_reasoning_tokens:
                response_json = {
                    "proposed_lin_str_eq": "Error during LLM call",
                }
            else:
                response_json = {
                    "plausibility": "Error: " + str(e),
                    "proposed_lin_str_eq": "Error during LLM call",
                }

        if debug_print:
            print("*****MODEL (parsed by instructor)*****")
            print(json.dumps(response_json, indent=2))

        response_history.append(response_json)

    df = pd.DataFrame(response_history)
    return df
