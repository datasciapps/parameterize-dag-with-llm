import datetime

import instructor
from custom_display_utility import display
from dag_module import DAG
from dag_traversal_utility import GeneralDAGData, compile_dag_metadata
from llm_integration import run_llm_elicitation
from llm_response_parser import convert_terms_to_coeffient_df, split_equations_to_terms
from prompt_generator import PromptPerNode
from validator_utlity import symbolic_range_validator
from visualization_utility import visualize_full_dag_effects


def parameterize_dag(
    education_wage_data: GeneralDAGData,
    include_hard_constraints: bool,
    client: instructor.AsyncInstructor,
    model_dependent_config: dict,
    instructor_model_name: str,
) -> dict:
    all_llm_responses_dfs = []  # This will store the *final* LLM response for each scenario (after validation passes)
    all_coefficients_dfs = []  # This will store the *final* coefficients for each scenario (after validation passes)
    all_scenario_validation_success = []  # New list to store validation success status for each scenario

    # # Experimental id
    exp_id: str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # logger = logging.getLogger("customlogger")
    # # logging.basicConfig(filename=f'./output/exp_{exp_id}.log', level=logging.DEBUG)
    # # logging.info(f'[*****Experiment ID: {exp_id} started.****')
    # log_file_path =  f'./output/exp_{exp_id}.log'

    # file_handler = logging.FileHandler(log_file_path)
    # file_handler.setLevel(logging.INFO)

    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # file_handler.setFormatter(formatter)

    # logger.addHandler(file_handler)
    # logger.info(f'[*****Experiment ID: {exp_id} started.****')

    print(f"[*****Experiment ID: {exp_id} started.****")
    print(f"Using Instructor Model: {instructor_model_name}")

    education_wage_dag = DAG(
        education_wage_data.all_nodes,
        education_wage_data.raw_edges,
        education_wage_data.node_descriptions,
        education_wage_data.node_lower_bound,
        education_wage_data.node_upper_bound,
    )

    education_wage_dag.visualize_dag(exp_id=exp_id)
    # Traverses raw edge format DAG and provides a list so that we can call the LLM calling later.
    dag_relationships = education_wage_dag.traverse_nodes()
    print("\n--- DAG Parent-Child Relationships ---")
    scenarios = compile_dag_metadata(
        education_wage_data, dag_relationships, include_hard_constraints
    )

    # Build a mapping of parameterized equations as we process scenarios
    # This will store the final validated equations for each node
    parameterized_equations = {}

    MAX_RETRIES = (
        5  # Set the maximum number of retries for LLM elicitation per scenario
    )

    for scenario_idx, scenario_to_process in enumerate(scenarios):
        print(f"\n{'=' * 80}")
        print(
            f"[SCENARIO {scenario_idx}] Starting processing for target variable: {scenario_to_process['target_variable_name']}"
        )
        print(f"{'=' * 80}\n")

        current_feedback_message = None  # Initialize feedback for the current scenario

        iteration_count = 0
        scenario_iteration_history = []  # New list to store history for *this* scenario's iterations

        # Variables to store the *last successfully validated* results for visualization outside the loop
        last_validated_coefficients_df = None
        last_validated_llm_responses_df = None
        current_scenario_succeeded = (
            False  # Flag to track if this scenario ultimately succeeded validation
        )

        while iteration_count < MAX_RETRIES:
            iteration_count += 1
            print(
                f"\n[SCENARIO {scenario_idx}, ITERATION {iteration_count}] Eliciting LLM response..."
            )

            prompt_generator = PromptPerNode(
                primary_domain_name=scenario_to_process["primary_domain_name"],
                secondary_domain_name=scenario_to_process["secondary_domain_name"],
                target_variable_name=scenario_to_process["target_variable_name"],
                direct_parent_variables=scenario_to_process["direct_parent_variables"],
                node_descriptions=scenario_to_process[
                    "node_descriptions"
                ],  # Include node descriptions here
                node_lower_bounds=scenario_to_process["node_lower_bounds"],
                node_upper_bounds=scenario_to_process["node_upper_bounds"],
                include_constraints_in_prompt=include_hard_constraints,
                feedback_message=current_feedback_message,  # Pass feedback message to the prompt generator
                phenomenon_overview=education_wage_data.phenomenon_overview,  # Pass phenomenon_overview
                dag=education_wage_dag,  # Pass the DAG to detect parent-parent relationships
                parameterized_equations=parameterized_equations,  # Pass already-parameterized equations
                include_parent_relationships=scenario_to_process.get("include_parent_relationships", True),  # Pass toggle flag, default to True
            )
            # --- LLM Loop ---

            elicitation_prompt = prompt_generator.get_full_prompt()
            llm_responses_df = run_llm_elicitation(
                client=client,
                elicitation_prompt=elicitation_prompt,
                scenario_to_process=scenario_to_process,
                model_dependent_config=model_dependent_config,
                wait_sec_per_chat=0.2,
                debug_print=True,
                num_responses_per_prompt=1,
            )
            llm_responses_df["scenario_idx"] = scenario_idx
            # Save the LLM responses DataFrame for this iteration but silence print since others will print it
            display(llm_responses_df, "llm_resp_df", exp_id=exp_id, silence_print=True)

            # timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            # llm_responses_df.to_csv(f'llm_responses_{scenario_idx}_{timestamp}.csv', index=False) # Keep this for saving individual responses for debugging if needed

            print(
                f"[SCENARIO {scenario_idx}, ITERATION {iteration_count}] --- Splitting equation terms ---"
            )
            split_terms = split_equations_to_terms(
                llm_responses_df,
                scenario_to_process["target_variable_name"],
                verbose=True,
            )

            print(
                f"[SCENARIO {scenario_idx}, ITERATION {iteration_count}] --- Converting terms to coefficients DataFrame ---"
            )
            coefficients_df = convert_terms_to_coeffient_df(
                split_terms,
                scenario_to_process["direct_parent_variables"],
                verbose=True,
                exp_id=exp_id,
            )

            validation_result = None  # Initialize to None

            assert not coefficients_df.empty
            # Parsed coefficients including intercept should match number of parents + 1
            assert len(coefficients_df.columns.to_list()) == (
                len(scenario_to_process["direct_parent_variables"]) + 1
            )

            if not coefficients_df.empty:
                proposed_equation_str = llm_responses_df.iloc[0]["proposed_lin_str_eq"]
                validation_result = symbolic_range_validator(
                    coefficients_df,
                    scenario_to_process["direct_parent_variables"],
                    scenario_to_process["target_variable_name"],
                    scenario_to_process["node_lower_bounds"],
                    scenario_to_process["node_upper_bounds"],
                    proposed_equation=proposed_equation_str,  # Pass the proposed equation
                )
                print("--- Full Validation Log ---")
                print(validation_result["validation_message"])
                print("--- Validation Summary ---")
                print(validation_result["summary_message"])

                # Store iteration history
                scenario_iteration_history.append(
                    {
                        "iteration_num": iteration_count,
                        "llm_response_df": llm_responses_df.copy(),  # Store a copy to avoid modification issues
                        "coefficients_df": coefficients_df.copy(),
                        "validation_result": validation_result.copy(),  # Store a copy
                    }
                )

                if validation_result["validated"]:
                    print(
                        f"[SCENARIO {scenario_idx}, ITERATION {iteration_count}] Validation passed - moving on to next scenario"
                    )
                    all_llm_responses_dfs.append(
                        llm_responses_df
                    )  # Now append the validated response
                    all_coefficients_dfs.append(
                        coefficients_df
                    )  # Now append the validated coefficients
                    last_validated_coefficients_df = (
                        coefficients_df  # Store for outside visualization
                    )
                    last_validated_llm_responses_df = (
                        llm_responses_df  # Store for outside visualization
                    )
                    # Store the parameterized equation for this node for future reference
                    parameterized_equations[scenario_to_process["target_variable_name"]] = proposed_equation_str
                    current_scenario_succeeded = True  # Mark as successful
                    break  # Exit while loop for current scenario
                else:
                    print(
                        f"[SCENARIO {scenario_idx}, ITERATION {iteration_count}] Validation failed - elicitation needs to be done again"
                    )
                    current_feedback_message = validation_result[
                        "summary_message"
                    ]  # Update feedback for next iteration
                    # Continue loop for next iteration
            else:
                print(
                    f"[SCENARIO {scenario_idx}, ITERATION {iteration_count}] Warning: Coefficients DataFrame is empty. Cannot perform validation. Retrying LLM."
                )
                summary_message_empty_coeff = "Warning: Coefficients DataFrame is empty. Cannot perform validation. Retrying LLM."
                # If coefficients_df is empty, proposed_lin_str_eq might not be directly available, or could be malformed.
                # Attempt to get it if possible, otherwise note its absence.
                proposed_equation_str = (
                    llm_responses_df.iloc[0]["proposed_lin_str_eq"]
                    if not llm_responses_df.empty
                    and "proposed_lin_str_eq" in llm_responses_df.iloc[0]
                    else "N/A (equation parsing failed)"
                )
                summary_message_empty_coeff_with_eq = f"{summary_message_empty_coeff}\nProposed Equation: {proposed_equation_str}"

                scenario_iteration_history.append(
                    {
                        "iteration_num": iteration_count,
                        "llm_response_df": llm_responses_df.copy(),
                        "coefficients_df": coefficients_df.copy(),  # Might be empty
                        "validation_result": {
                            "validation_message": summary_message_empty_coeff_with_eq,
                            "validated": False,
                            "summary_message": summary_message_empty_coeff_with_eq,
                        },
                    }
                )
                current_feedback_message = summary_message_empty_coeff_with_eq  # Update feedback for next iteration
                # Continue loop for next iteration

        # After the while loop finishes:
        # If no successful validation occurred, use the last proposal from iteration history
        if not current_scenario_succeeded and scenario_iteration_history:
            print(
                f"\n[SCENARIO {scenario_idx}] Max retries ({MAX_RETRIES}) reached without successful validation. Using the last proposal."
            )
            last_iteration_data = scenario_iteration_history[-1]
            last_validated_coefficients_df = last_iteration_data["coefficients_df"]
            last_validated_llm_responses_df = last_iteration_data["llm_response_df"]
            # Also add to the 'final' lists if not already added by successful validation
            all_llm_responses_dfs.append(last_validated_llm_responses_df)
            all_coefficients_dfs.append(last_validated_coefficients_df)
            # Store the equation from the last proposal
            if (
                not last_validated_llm_responses_df.empty
                and "proposed_lin_str_eq" in last_validated_llm_responses_df.columns
            ):
                parameterized_equations[scenario_to_process["target_variable_name"]] = (
                    last_validated_llm_responses_df.iloc[0]["proposed_lin_str_eq"]
                )
            # current_scenario_succeeded remains False
        elif not current_scenario_succeeded and not scenario_iteration_history:
            print(
                f"\n[SCENARIO {scenario_idx}] No proposals generated for this scenario after all retries."
            )

        # Record the final success status for this scenario
        all_scenario_validation_success.append(current_scenario_succeeded)

        # --- Visualization and Effect Sizes (This block will now always execute if there's any proposal) ---
        if (
            last_validated_coefficients_df is not None
            and not last_validated_coefficients_df.empty
        ):
            effect_sizes = {}
            for parent_var_name in scenario_to_process["direct_parent_variables"]:
                col_name = f"beta_{parent_var_name}"
                if col_name in last_validated_coefficients_df.columns:
                    effect_sizes[parent_var_name] = last_validated_coefficients_df.loc[
                        0, col_name
                    ]

            print(
                f"[EFFECT_SIZES {scenario_idx}] Extracted for scenario:", effect_sizes
            )
            print(
                f"\n[VISUALIZATION {scenario_idx}] --- Parent-Child Relationship with Effect Sizes ---"
            )
            display(
                prompt_generator.visualize_parent_child_relationship(
                    effect_sizes=effect_sizes
                ),
                output_file_postfix="viz_par_chil",
                exp_id=exp_id,
            )
        else:
            print(
                f"[SCENARIO {scenario_idx}] No valid or last-resort coefficients obtained for this scenario after all retries, skipping visualization."
            )

        # Optional: print or save the iteration history for this scenario
        print(f"\n[SCENARIO {scenario_idx}] Iteration history for this scenario:")
        for entry in scenario_iteration_history:
            print(
                f"  Iteration {entry['iteration_num']}: Validated = {entry['validation_result']['validated']}, Summary = {entry['validation_result']['summary_message']}"
            )

    visualize_full_dag_effects(
        scenarios,
        all_coefficients_dfs,
        education_wage_data,
        all_scenario_validation_success,
        exp_id=exp_id,
        model_name=instructor_model_name,
    )
    return {
        "all_llm_responses_dfs": all_llm_responses_dfs,
        "all_coefficients_dfs": all_coefficients_dfs,
        "all_scenario_validation_success": all_scenario_validation_success,
        "scenarios": scenarios,
        "education_wage_data": education_wage_data,
    }
