"""dag_traversal_utility.py
"""
class GeneralDAGData:
    def __init__(self, all_nodes: set, raw_edges: list[tuple[str, str]], node_descriptions: dict[str, str], primary_domain_name: str, secondary_domain_name: str, node_lower_bound: dict[str, float], node_upper_bound: dict[str, float], ground_truth_effect_sizes: dict[tuple[str, str], float], phenomenon_overview: str):
        self.all_nodes = all_nodes
        self.raw_edges = raw_edges
        self.node_descriptions = node_descriptions
        self.primary_domain_name = primary_domain_name
        self.secondary_domain_name = secondary_domain_name
        self.node_lower_bound = node_lower_bound
        self.node_upper_bound = node_upper_bound
        self.ground_truth_effect_sizes = ground_truth_effect_sizes
        self.phenomenon_overview = phenomenon_overview

def compile_dag_metadata(dag_data: GeneralDAGData, dag_relationships: list[dict], include_hard_constraints: bool) -> list[dict]:
    scenarios = []
    for relation in dag_relationships:
        print(relation)
        compiled_variable_description = {
            "primary_domain_name": dag_data.primary_domain_name, # Referencing from dag_data instance
            "secondary_domain_name": dag_data.secondary_domain_name, # Referencing from dag_data instance
            "target_variable_name": relation["target_variable_name"],
            "direct_parent_variables": relation["direct_parent_variables"],
            "node_descriptions": dag_data.node_descriptions, # Include node descriptions here
            "node_lower_bounds": dag_data.node_lower_bound,
            "node_upper_bounds": dag_data.node_upper_bound,
            "include_constraints_in_prompt": include_hard_constraints
        }
        print(compiled_variable_description)
        if len(relation["direct_parent_variables"]) > 0:
            scenarios.append(compiled_variable_description)

    print(scenarios)
    return scenarios
