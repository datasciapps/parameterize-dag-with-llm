import pandas as pd


VALIDATION_TOLERANCE = 1e-9


def compute_predicted_target_range(
    intercept: float,
    parent_coefficients: dict[str, float],
    direct_parent_variables: list[str],
    node_lower_bounds: dict,
    node_upper_bounds: dict,
) -> dict:
    min_predicted_target = intercept
    max_predicted_target = intercept
    validation_messages = []

    for parent_variable in direct_parent_variables:
        coefficient = parent_coefficients.get(parent_variable)

        if coefficient is None:
            validation_messages.append(
                f"[VALIDATOR] Warning: Coefficient for parent variable '{parent_variable}' not found. Skipping."
            )
            continue

        parent_lower_bound = node_lower_bounds.get(parent_variable)
        parent_upper_bound = node_upper_bounds.get(parent_variable)

        if parent_lower_bound is None or parent_upper_bound is None:
            validation_messages.append(
                f"[VALIDATOR] Warning: Bounds for parent variable '{parent_variable}' not found. Skipping calculation for this parent."
            )
            continue

        if coefficient >= 0:
            min_predicted_target += coefficient * parent_lower_bound
            max_predicted_target += coefficient * parent_upper_bound
        else:
            min_predicted_target += coefficient * parent_upper_bound
            max_predicted_target += coefficient * parent_lower_bound

    return {
        "min_predicted_target": min_predicted_target,
        "max_predicted_target": max_predicted_target,
        "validation_messages": validation_messages,
    }


def compute_range_midpoint(lower_bound: float, upper_bound: float) -> float:
    return (lower_bound + upper_bound) / 2.0


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

    intercept = llm_coefficients.get("beta_0", 0.0)
    parent_coefficients = {
        parent_variable: llm_coefficients.get(f"beta_{parent_variable}")
        for parent_variable in direct_parent_variables
    }

    predicted_range = compute_predicted_target_range(
        intercept=intercept,
        parent_coefficients=parent_coefficients,
        direct_parent_variables=direct_parent_variables,
        node_lower_bounds=node_lower_bounds,
        node_upper_bounds=node_upper_bounds,
    )
    validation_messages.extend(predicted_range["validation_messages"])
    min_predicted_target = predicted_range["min_predicted_target"]
    max_predicted_target = predicted_range["max_predicted_target"]

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
        if min_predicted_target < (target_hard_lower_bound - VALIDATION_TOLERANCE):
            inconsistencies.append(
                f"Predicted minimum ({min_predicted_target:.2f}) for '{target_variable_name}' is below its hard lower bound ({target_hard_lower_bound})."
            )
            is_validated = False
        if max_predicted_target > (target_hard_upper_bound + VALIDATION_TOLERANCE):
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


def _run_self_test() -> None:
    parent_coefficients = {"A": 0.5, "B": -0.25}
    predicted_range = compute_predicted_target_range(
        intercept=2.0,
        parent_coefficients=parent_coefficients,
        direct_parent_variables=["A", "B"],
        node_lower_bounds={"A": 0.0, "B": 10.0, "Y": 0.0},
        node_upper_bounds={"A": 4.0, "B": 14.0, "Y": 10.0},
    )

    assert predicted_range["min_predicted_target"] == 2.0 + (0.5 * 0.0) + (-0.25 * 14.0)
    assert predicted_range["max_predicted_target"] == 2.0 + (0.5 * 4.0) + (-0.25 * 10.0)
    assert compute_range_midpoint(2.0, 6.0) == 4.0

    coefficients_df = pd.DataFrame([{"beta_0": 4.0, "beta_A": 0.5, "beta_B": -0.25}])
    validation_result = symbolic_range_validator(
        coefficients_df=coefficients_df,
        direct_parent_variables=["A", "B"],
        target_variable_name="Y",
        node_lower_bounds={"A": 0.0, "B": 10.0, "Y": 0.0},
        node_upper_bounds={"A": 4.0, "B": 14.0, "Y": 10.0},
        proposed_equation="Y = 4.0*1 + 0.5*A + -0.25*B + E_Y",
    )
    assert validation_result["validated"] is True, validation_result

    print("validator_utlity self-test passed")


if __name__ == "__main__":
    _run_self_test()
