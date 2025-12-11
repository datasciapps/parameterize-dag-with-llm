from pydantic import BaseModel
import pandas as pd
from google.genai import types
import instructor
import time
import json


# Pydantic model for LLM response
class LLMParamResponse(BaseModel):
    plausibility: str
    proposed_lin_str_eq: str



def run_llm_elicitation(
    num_responses_per_prompt: int = 5,
    debug_print=True,
    wait_sec_per_chat=1,
    elicitation_prompt: str = "",
    scenario_to_process: dict = None,
) -> pd.DataFrame:
    """Runs the LLM elicitation process for a single prompt multiple times to collect varied responses."""
    assert len(elicitation_prompt) > 0
    assert scenario_to_process is not None

    # Configuration for Gemini model, including thinking_config
    gemini_config = types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
    )

    # Initialize instructor client
    client = instructor.from_provider(
        "google/gemini-2.5-flash",
    )

    if num_responses_per_prompt > 1:
        raise NotImplementedError("Currently only single response is supported.")

    response_history: list[dict] = []
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
            response_obj = client.create(
                response_model=LLMParamResponse,
                messages=[
                    {
                        "role": "user",
                        "content": elicitation_prompt,
                    }
                ],
                config=gemini_config,
            )
            # Convert the Pydantic model instance to a dictionary for history storage
            response_json = response_obj.model_dump()
            proposed_lin_str_eq: str = response_json.get("proposed_lin_str_eq", "")
            print("[Run LLM Elicitation] Proposed Linear String Equation (early validation):")    
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
