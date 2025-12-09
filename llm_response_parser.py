import pandas as pd
import re
import json
from custom_display_utility import display


def split_equation(equation_str_to_split, verbose=False):  # Renamed for clarity
    if verbose:
        print(
            f"Equation part for splitting (after error term removal): {equation_str_to_split}"
        )

    # The input `equation_str_to_split` is already the RHS, cleaned of target variable and error term.
    equation_rhs = equation_str_to_split.strip()

    if not equation_rhs:  # Handle empty string after cleaning
        return []

    # Split by ' + ' or ' - ' but capture the delimiter as well.
    # This regex ensures that signs attached to numbers (e.g., -0.5) are not split,
    # but operators between terms are.
    split_parts = re.split(r"(\s*(?<![\d.])\+\s*|\s*(?<![\d.])-\s*)", equation_rhs)
    split_parts = [
        p.strip() for p in split_parts if p.strip()
    ]  # Remove any empty strings resulting from the split

    processed_terms = []
    if not split_parts:
        return []

    current_term_idx = 0
    # Handle the first term. If it starts with a sign, combine it with the next part.
    # E.g., for "-5*1 + 1*EDUC", split_parts could be ['-', '5*1', '+', '1*EDUC']
    # If it's "5*1 + 1*EDUC", split_parts could be ['5*1', '+', '1*EDUC']
    if split_parts[0] in ["+", "-"]:
        # If the first part is an operator, and there's a subsequent term, combine them.
        if len(split_parts) > 1:
            processed_terms.append(split_parts[0] + split_parts[1])
            current_term_idx = 2
        else:
            # Malformed: A single operator as the only content.
            if verbose:
                print(
                    f"Warning: Malformed equation string '{equation_str_to_split}' resulted in only an operator: {split_parts[0]}"
                )
            return []  # Return empty if it's just an operator
    else:
        # The first part is a term, implicitly positive.
        processed_terms.append(split_parts[0])
        current_term_idx = 1

    # Process remaining terms
    while current_term_idx < len(split_parts):
        operator = split_parts[current_term_idx]
        # Ensure there's a term after the operator
        if current_term_idx + 1 < len(split_parts):
            term_value = split_parts[current_term_idx + 1]
            processed_terms.append(operator + term_value)
        else:
            # This should ideally not happen if equation_str_to_split is properly formed
            # (e.g., doesn't end with an operator after cleaning).
            if verbose:
                print(
                    f"Warning: Trailing operator '{operator}' detected at the end of equation part: {equation_str_to_split}. Ignoring."
                )
        current_term_idx += 2

    # Remove all spaces from the processed terms
    final_terms = [term.replace(" ", "") for term in processed_terms if term.strip()]

    if verbose:
        print(f"Split terms: {final_terms}")
    return final_terms


def split_equations_to_terms(
    llm_responses_df: pd.DataFrame, target_variable_name: str, verbose=False
) -> list[list[str]]:
    split_terms: list[list[str]] = []

    for i, lin_eq_raw in enumerate(llm_responses_df["proposed_lin_str_eq"].to_list()):
        lin_eq = ""
        if isinstance(lin_eq_raw, dict):
            lin_eq = lin_eq_raw.get(
                "equation", ""
            )  # Extract the 'equation' string if it's a dict
            assert lin_eq, (
                f"Index {i}: Dictionary found but 'equation' key missing or empty: {lin_eq_raw}"
            )
        elif isinstance(lin_eq_raw, str):
            try:
                # Attempt to parse the raw string as JSON. If successful, it's a JSON string, not an equation.
                json.loads(lin_eq_raw)
                assert False, (
                    f"Index {i}: Raw string is a complete JSON object, expected equation string: {lin_eq_raw}"
                )
            except json.JSONDecodeError:
                # If it's not a complete JSON object, then it might be a valid equation string or contain nested JSON.
                lin_eq = lin_eq_raw
        else:
            assert False, (
                f"Index {i}: Expected string or dict, got {type(lin_eq_raw).__name__}: {lin_eq_raw}"
            )

        # Assert that an equals sign exists in the equation
        assert "=" in lin_eq, f"Index {i}: No '=' found in equation: {lin_eq_raw}"

        # Extract RHS (everything after '=')
        equation_rhs_full = lin_eq.split("=", 1)[1].strip()

        # Find and remove the error term (e.g., E_GM) and its preceding operator
        # The pattern now explicitly re-uses the robust operator matching and captures the error term separately
        error_term_pattern = r"(\s*(?<![\d.])\+\s*|\s*(?<![\d.])-\s*)?(E_[A-Za-z0-9_]+)"
        error_term_match = re.search(error_term_pattern, equation_rhs_full)

        if not error_term_match:
            # If no error term found, this is an assertion failure as per the problem definition
            assert False, (
                f"Index {i}: No error term (e.g., E_Y or E_VARIABLE) found in equation: {lin_eq_raw}"
            )

        # Remove the matched error term (group 0 is the full match including operator if any)
        equation_cleaned_rhs = re.sub(error_term_pattern, "", equation_rhs_full).strip()

        # Clean up any potential trailing operators that might be left (e.g., "TERM + ")
        # Re-use the robust operator matching pattern for trailing operators
        equation_cleaned_rhs = re.sub(
            r"(\s*(?<![\d.])\+\s*|\s*(?<![\d.])-\s*)$", "", equation_cleaned_rhs
        ).strip()

        # Now pass the cleaned equation string (which should only contain numerical terms) to split_equation
        terms = split_equation(equation_cleaned_rhs, verbose=verbose)
        split_terms.append(terms)
    if verbose:
        print(split_terms)
    return split_terms


def extract_coefficient(term, variable_name):
    # This regex looks for a number (int or float, possibly negative)
    # followed by '*' and then the variable_name.
    # It also handles cases like '-0.5*SIBLINGS' where the '-' is part of the number.
    match = re.match(
        r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\*" + re.escape(variable_name), term
    )
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def extract_intercept(term):
    if "*1" in term:
        value_str = term.split("*1")[0]
        try:
            # Handle potential leading '+' or '-' in the constant term
            if value_str.startswith("+"):
                value_str = value_str[1:]
            return float(value_str)
        except ValueError:
            return None  # Handle cases where conversion to float fails
    return None


def convert_terms_to_coeffient_df(
    split_terms: list[list[str]], scenario_parents: list[str], exp_id: str, verbose=False
) -> pd.DataFrame:
    coefficients_list = []

    for terms in split_terms:
        coefficients = {}
        for term in terms:
            if "*1" in term:
                coefficients["beta_0"] = extract_intercept(term)
            for parent_var_name in scenario_parents:
                coeff = extract_coefficient(term, parent_var_name)
                if coeff is not None:
                    coefficients[f"beta_{parent_var_name}"] = coeff

        # Assert that all scenario_parents have a corresponding beta coefficient
        for parent_var_name in scenario_parents:
            assert f"beta_{parent_var_name}" in coefficients, (
                f"Missing coefficient for parent variable '{parent_var_name}' in LLM response: {terms}"
            )

        coefficients_list.append(coefficients)

    coefficients_df = pd.DataFrame(coefficients_list)
    if verbose:
        display(coefficients_df, "coeff_df", exp_id=exp_id)
    else:
        display(coefficients_df.head(), "coeff_df_head", exp_id=exp_id)
    return coefficients_df

