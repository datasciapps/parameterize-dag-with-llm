import pandas as pd


def symbolic_range_validator(
    coefficients_df: pd.DataFrame,
    direct_parent_variables: list[str],
    target_variable_name: str,
    node_lower_bounds: dict,
    node_upper_bounds: dict,
    proposed_equation: str,
) -> dict:
    validation_messages = []
    is_validated = True
    summary_message = ""

    validation_messages.append(
        f"[VALIDATOR] Running symbolic range validation for {target_variable_name}"
    )

    if coefficients_df.empty or len(coefficients_df) == 0:
        msg = "[VALIDATOR] Warning: No coefficients found for validation."
        validation_messages.append(msg)
        summary_message = f"{msg}\nProposed Equation: {proposed_equation}"
        return {
            "validation_message": "\n".join(validation_messages),
            "validated": False,
            "summary_message": summary_message,
        }

    # Assuming the first row contains the coefficients from the LLM
    llm_coefficients = coefficients_df.iloc[0]

    # 2. Extract intercept (beta_0)
    intercept = llm_coefficients.get("beta_0", 0.0)

    # 3. Initialize min_predicted_target and max_predicted_target with the intercept value
    min_predicted_target = intercept
    max_predicted_target = intercept

    # 4. Iterate through each parent_variable in direct_parent_variables
    for parent_variable in direct_parent_variables:
        coefficient = llm_coefficients.get(f"beta_{parent_variable}")

        if coefficient is None:
            msg = f"[VALIDATOR] Warning: Coefficient for parent variable '{parent_variable}' not found. Skipping."
            validation_messages.append(msg)
            # is_validated = False # Keep as True if missing coefficient just means no contribution to range
            continue

        parent_lower_bound = node_lower_bounds.get(parent_variable)
        parent_upper_bound = node_upper_bounds.get(parent_variable)

        if parent_lower_bound is None or parent_upper_bound is None:
            msg = f"[VALIDATOR] Warning: Bounds for parent variable '{parent_variable}' not found. Skipping calculation for this parent."
            validation_messages.append(msg)
            is_validated = True  # If no comparisons possible due to no parent ranges available, treat as success
            # continue

        if coefficient >= 0:
            min_predicted_target += coefficient * parent_lower_bound
            max_predicted_target += coefficient * parent_upper_bound
        else:
            min_predicted_target += coefficient * parent_upper_bound
            max_predicted_target += coefficient * parent_lower_bound

    # 5. Retrieve hard bounds for the target_variable_name
    target_hard_lower_bound = node_lower_bounds.get(target_variable_name)
    target_hard_upper_bound = node_upper_bounds.get(target_variable_name)

    validation_messages.append(
        f"[VALIDATOR] Predicted range for '{target_variable_name}': [{min_predicted_target:.2f}, {max_predicted_target:.2f}]"
    )

    if target_hard_lower_bound is None or target_hard_upper_bound is None:
        msg = f"[VALIDATOR] Warning: Hard constraints for target variable '{target_variable_name}' not found. Cannot compare. Validation considered passed as no constraints were violated."
        validation_messages.append(msg)
        # is_validated remains True as per user request if no constraints are present
        summary_message = f"[VALIDATOR] PASSED (No Constraints): No hard constraints for '{target_variable_name}' were found for comparison.\nProposed Equation: {proposed_equation}"
    else:
        validation_messages.append(
            f"[VALIDATOR] Hard constraint range for '{target_variable_name}': [{target_hard_lower_bound}, {target_hard_upper_bound}]"
        )

        # 6. Compare predicted range with hard constraints and 7. print inconsistencies
        inconsistencies = []
        if min_predicted_target < target_hard_lower_bound:
            inconsistencies.append(
                f"Predicted minimum ({min_predicted_target:.2f}) for '{target_variable_name}' is below its hard lower bound ({target_hard_lower_bound})."
            )
            is_validated = False
        if max_predicted_target > target_hard_upper_bound:
            inconsistencies.append(
                f"Predicted maximum ({max_predicted_target:.2f}) for '{target_variable_name}' is above its hard upper bound ({target_hard_upper_bound})."
            )
            is_validated = False

        if inconsistencies:
            summary_message = f"[VALIDATOR] INCONSISTENCY for '{target_variable_name}': {'; '.join(inconsistencies)}\nProposed Equation: {proposed_equation}"
            validation_messages.append(summary_message)
        else:
            summary_message = f"[VALIDATOR] CONSISTENT: Predicted range [{min_predicted_target:.2f}, {max_predicted_target:.2f}] for '{target_variable_name}' is within its hard constraints.\nProposed Equation: {proposed_equation}"
            validation_messages.append(summary_message)

    return {
        "validation_message": "\n".join(validation_messages),
        "validated": is_validated,
        "summary_message": summary_message,
    }

