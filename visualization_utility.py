import pandas as pd
from dag_traversal_utility import GeneralDAGData
import datetime
import json
import numpy as np
import graphviz


def visualize_full_dag_effects(
    all_scenarios: list[dict],
    all_coefficients_dfs: list[pd.DataFrame],
    dag_data: GeneralDAGData,
    all_scenario_validation_success: list[bool],
    console_output_json: bool = False,
    save_json_to_file: bool = True,
) -> None:
    # Aggregate all effect sizes into a single dictionary (parent_name, child_name): effect_size
    all_effect_sizes_map = {}

    # Store effect sizes by target variable for ordering comparison
    llm_effects_by_target = {node_name: {} for node_name in dag_data.all_nodes}
    gt_effects_by_target = {node_name: {} for node_name in dag_data.all_nodes}

    for i, scenario_data in enumerate(all_scenarios):
        target_variable = scenario_data["target_variable_name"]
        coefficients_df = all_coefficients_dfs[i]

        if not coefficients_df.empty:
            for col in coefficients_df.columns:
                if col.startswith("beta_") and col != "beta_0":
                    parent_variable = col.replace("beta_", "")
                    effect_size = coefficients_df.loc[0, col]
                    all_effect_sizes_map[(parent_variable, target_variable)] = (
                        effect_size
                    )
                    llm_effects_by_target[target_variable][parent_variable] = (
                        effect_size
                    )

    # Populate gt_effects_by_target from dag_data.ground_truth_effect_sizes
    for (parent, child), gt_effect in dag_data.ground_truth_effect_sizes.items():
        if child in gt_effects_by_target:  # Ensure child is a node in the DAG
            gt_effects_by_target[child][parent] = gt_effect

    print("Aggregated Effect Sizes:", all_effect_sizes_map)

    # Calculate statistics to be displayed as a label
    stats_result = compute_graph_statistics(all_effect_sizes_map, dag_data)
    l2_norm_value = stats_result.get("l2_norm", "N/A")
    statistics_label_text = (
        f"L2 Norm of differences (LLM-elicited vs GT): {l2_norm_value} (Model: google/gemini-2.5-flash)\n"
        f"* indicates that parametrization feedback loop failed within loop budget.\n"
        f"Node Color Scheme:\n"
        f"- Lightgreen: Correct order of effect sizes from LLM vs GT (for >1 parents)\n"
        f"- Lightcoral: Incorrect order of effect sizes from LLM vs GT (for >1 parents)\n"
        f"- Lightgray: Single parent, no parents, or insufficient data for comparison"
    )

    dot = graphviz.Digraph(
        comment="Causal DAG", graph_attr={"rankdir": "TB", "overlap": "false"}
    )
    dot.attr(label=statistics_label_text, labelloc="t", labeljust="l", fontsize="12")

    # Determine node colors based on effect size ordering
    node_colors = {}
    for node_name in dag_data.all_nodes:
        # Find scenario data for the current node as target
        current_scenario = next(
            (s for s in all_scenarios if s["target_variable_name"] == node_name), None
        )

        if current_scenario:
            direct_parents = current_scenario["direct_parent_variables"]
        else:
            # If it's a root node, it won't be a target in any scenario
            direct_parents = []

        if len(direct_parents) <= 1:
            node_colors[node_name] = "lightgray"  # Changed black to lightgray
        else:
            current_target_gt_effects_for_node = {
                p: gt_effects_by_target[node_name].get(p) for p in direct_parents
            }
            current_target_llm_effects_for_node = {
                p: llm_effects_by_target[node_name].get(p) for p in direct_parents
            }

            # Filter out parents for which we don't have both GT and LLM effects
            # This ensures we only compare effects that are present in both ground truth and LLM output
            comparable_parents = [
                p
                for p in direct_parents
                if current_target_gt_effects_for_node[p] is not None
                and current_target_llm_effects_for_node[p] is not None
            ]

            if (
                len(comparable_parents) < len(direct_parents)
                or len(comparable_parents) < 2
            ):  # Need at least two parents to compare order
                node_colors[node_name] = "lightgray"
            else:
                # Sort parents by GT effect size (descending)
                sorted_gt_parents = sorted(
                    comparable_parents,
                    key=lambda p: current_target_gt_effects_for_node[p],
                    reverse=True,
                )
                # Sort parents by LLM effect size (descending)
                sorted_llm_parents = sorted(
                    comparable_parents,
                    key=lambda p: current_target_llm_effects_for_node[p],
                    reverse=True,
                )

                if sorted_gt_parents == sorted_llm_parents:
                    node_colors[node_name] = "lightgreen"  # Changed green to lightgreen
                else:
                    node_colors[node_name] = "lightcoral"  # Changed red to lightcoral

    for node_name in dag_data.all_nodes:
        color = node_colors.get(
            node_name, "lightgray"
        )  # Default to lightgray if not determined (e.g., root nodes without direct parents)
        dot.node(node_name, node_name, style="filled", fillcolor=color)

    for parent_name, child_name in dag_data.raw_edges:
        edge_label_parts = []

        scenario_index_for_child = -1
        for idx, scenario_data in enumerate(all_scenarios):
            if scenario_data["target_variable_name"] == child_name:
                scenario_index_for_child = idx
                break

        is_edge_scenario_successful = True
        if scenario_index_for_child != -1:
            is_edge_scenario_successful = all_scenario_validation_success[
                scenario_index_for_child
            ]

        if (parent_name, child_name) in all_effect_sizes_map:
            llm_effect_size = all_effect_sizes_map[(parent_name, child_name)]
            prefix = "" if is_edge_scenario_successful else "*"
            edge_label_parts.append(
                f"{prefix}LLM={llm_effect_size:e}"
            )  # Changed to scientific notation

        if (parent_name, child_name) in dag_data.ground_truth_effect_sizes:
            gt_effect_size = dag_data.ground_truth_effect_sizes[
                (parent_name, child_name)
            ]
            edge_label_parts.append(
                f"GT={gt_effect_size:e}"
            )  # Changed to scientific notation

        edge_label = "\n".join(edge_label_parts) if edge_label_parts else ""

        dot.edge(parent_name, child_name, label=edge_label)

    filename = "full_dag_with_effect_sizes"
    format = "png"
    try:
        dot.render(filename, format=format, cleanup=True)
        full_filename = f"{filename}.{format}"
        print(f"Full DAG visualization with effect sizes saved to '{full_filename}'")
        display(Image(filename=full_filename))
    except Exception as e:
        print(f"Error rendering full DAG visualization: {e}")

    # Prepare data for JSON output
    json_output_data = {
        "all_scenarios": all_scenarios,
        "all_coefficients_dfs": [df.to_dict("records") for df in all_coefficients_dfs],
        "dag_data": {
            "all_nodes": list(dag_data.all_nodes),
            "raw_edges": dag_data.raw_edges,
            "node_descriptions": dag_data.node_descriptions,
            "primary_domain_name": dag_data.primary_domain_name,
            "secondary_domain_name": dag_data.secondary_domain_name,
            "node_lower_bound": dag_data.node_lower_bound,
            "node_upper_bound": dag_data.node_upper_bound,
            "ground_truth_effect_sizes": {
                f"{k[0]}->{k[1]}": v
                for k, v in dag_data.ground_truth_effect_sizes.items()
            },
            "phenomenon_overview": dag_data.phenomenon_overview,
        },
        "all_scenario_validation_success": all_scenario_validation_success,
        "all_effect_sizes_map": {
            f"{k[0]}->{k[1]}": v for k, v in all_effect_sizes_map.items()
        },
        "llm_effects_by_target": llm_effects_by_target,
        "gt_effects_by_target": gt_effects_by_target,
        "node_colors": node_colors,
        "statistics_label_text": statistics_label_text,
        "l2_norm_value": l2_norm_value,
    }

    # Generate a timestamp for the JSON filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"full_dag_visualization_snapshot_{timestamp}.json"

    if save_json_to_file:
        with open(json_filename, "w") as f:
            json.dump(json_output_data, f, indent=2, cls=CustomJsonEncoder)
        print(f"Visualization data saved to '{json_filename}'")

    if console_output_json:
        print("\n--- Visualization Data (JSON) ---")
        print(json.dumps(json_output_data, indent=2, cls=CustomJsonEncoder))


def compute_graph_statistics(
    all_effect_sizes_map, dag_data: GeneralDAGData, normalize_effect_per_node=False
) -> dict:
    # --- Comparison Logic --- (using L2 norm as requested)
    differences_squared = []

    print("\n--- Comparing LLM Elicited Effects with Ground Truth ---")
    if normalize_effect_per_node:
        raise NotImplementedError
    for (parent, child), llm_effect in all_effect_sizes_map.items():
        ground_truth_key = (parent, child)
        assert ground_truth_key in dag_data.ground_truth_effect_sizes, (
            f"Warning: Ground truth for {parent} -> {child} not found. LLM effect: {llm_effect:.2f}"
        )
        gt_effect = dag_data.ground_truth_effect_sizes[ground_truth_key]
        diff = llm_effect - gt_effect
        differences_squared.append(diff**2)
        print(
            f"Effect {parent} -> {child}: LLM={llm_effect:.2f}, GT={gt_effect:.2f}, Diff={diff:.2f}"
        )

    # Calculate the L2 norm (Euclidean distance)
    if differences_squared:
        l2_norm = np.sqrt(np.sum(differences_squared))
        print(f"\nCalculated L2 Norm of differences: {l2_norm:.4f}")
        return {"l2_norm": str(l2_norm)}
    else:
        print("No common effects to compare. L2 Norm cannot be calculated.")
        return {"l2_norm": str(None)}


# compute_graph_statistics(all_effect_sizes_map)



# Custom JSON encoder to handle non-serializable types like numpy floats and sets
class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float64):
            return float(obj)
        if isinstance(obj, set):
            return list(obj)
        # Convert tuple keys in dictionaries to strings
        if isinstance(obj, dict):
            return {str(k): v for k, v in obj.items()}
        return json.JSONEncoder.default(self, obj)