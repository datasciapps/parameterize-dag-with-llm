# dag_module.py
"""Module defining classes for Directed Acyclic Graph (DAG) representation and manipulation, DAGNode and DAG.
"""
from collections import deque
import graphviz

class DAGNode:
    def __init__(self, name):
        self.name = name
        self.parents = []
        self.children = []

    def __repr__(self):
        return f"DAGNode('{self.name}')"

    def add_parent(self, parent_node):
        if parent_node not in self.parents:
            self.parents.append(parent_node)

    def add_child(self, child_node):
        if child_node not in self.children:
            self.children.append(child_node)


class DAG:
    def __init__(self, all_nodes, raw_edges, node_descriptions: dict = None, lower_bound: dict = None, upper_bound: dict = None):
        self.nodes = {}
        self.in_degree = {node_name: 0 for node_name in all_nodes}

        if node_descriptions is None:
            node_descriptions = {}

        # Assertion: Ensure every node in all_nodes has a description
        for node_name in all_nodes:
            if node_name not in node_descriptions:
                raise ValueError(f"Missing description for node '{node_name}' in node_descriptions.")

        self.node_descriptions = node_descriptions

        self.lower_bound = lower_bound if lower_bound is not None else {}
        # Optional: You might want to validate that keys in lower_bound are indeed in all_nodes
        for lb_node in self.lower_bound:
            if lb_node not in all_nodes:
                raise ValueError(f"Lower bound provided for unknown node '{lb_node}'.")

        self.upper_bound = upper_bound if upper_bound is not None else {}
        # Optional: Validate that keys in upper_bound are indeed in all_nodes
        for ub_node in self.upper_bound:
            if ub_node not in all_nodes:
                raise ValueError(f"Upper bound provided for unknown node '{ub_node}'.")

        for node_name in all_nodes:
            self.nodes[node_name] = DAGNode(node_name)

        for parent_name, child_name in raw_edges:
            parent_node = self.nodes[parent_name]
            child_node = self.nodes[child_name]

            parent_node.add_child(child_node)
            child_node.add_parent(parent_node)
            self.in_degree[child_name] += 1

        print("[DAG] DAG class initialized with nodes and edges.")

    def get_node_description(self, node_name: str) -> str:
        """Returns the textual description for a given node."""
        return self.node_descriptions.get(node_name, f"No description available for {node_name}.")

    def get_lower_bound(self, node_name: str):
        """Returns the lower bound for a given node, or None if not specified."""
        return self.lower_bound.get(node_name, None)

    def get_upper_bound(self, node_name: str):
        """Returns the upper bound for a given node, or None if not specified."""
        return self.upper_bound.get(node_name, None)

    def topological_sort(self):
        queue = deque()
        current_in_degree = self.in_degree.copy()

        for node_name, degree in current_in_degree.items():
            if degree == 0:
                queue.append(self.nodes[node_name])

        sorted_nodes = []

        while queue:
            current_node = queue.popleft()
            sorted_nodes.append(current_node)

            for child_node in current_node.children:
                current_in_degree[child_node.name] -= 1

                if current_in_degree[child_node.name] == 0:
                    queue.append(child_node)

        if len(sorted_nodes) != len(self.nodes):
            print("[DAG] Warning: The DAG contains a cycle!")
            return []

        return sorted_nodes

    def traverse_nodes(self):
        print("[DAG] --- DAG Traversal from Top (Causes) to Bottom (Effects) ---\n")
        sorted_nodes = self.topological_sort()

        if not sorted_nodes:
            print("[DAG] Cannot traverse a graph with a cycle or no nodes.")
            return [] # Return empty list if no nodes or cycle

        relationships_list = []

        for node in sorted_nodes:
            if node.parents:
                print(f"[DAG] CHILD NODE: {node.name}")
                print(f"[DAG]   PARENTS ({len(node.parents)} direct causes):")
                for i, parent in enumerate(node.parents, 1):
                    print(f"[DAG]     {i}. {parent.name}")
            else:
                print(f"[DAG] ROOT NODE: {node.name} (No incoming edges)")
            print("[DAG] " + "-" * 20)

            relationships_list.append({
                "target_variable_name": node.name,
                "direct_parent_variables": [parent.name for parent in node.parents]
            })

        print("[DAG] Traversal Complete.")
        return relationships_list

    def visualize_dag(self, filename='dag_visualization', format='png', display_in_notebook=False):
        """Visualizes the DAG using graphviz and saves it to a file. Optionally displays it in the notebook."""
        dot = graphviz.Digraph(comment='Causal DAG', graph_attr={'rankdir': 'LR', 'overlap': 'false'})

        for node_name in self.nodes:
            dot.node(node_name, node_name)

        for node_name, node_obj in self.nodes.items():
            for child_node in node_obj.children:
                dot.edge(node_name, child_node.name)

        try:
            dot.render(filename, format=format, cleanup=True)
            full_filename = f"{filename}.{format}"
            print(f"[DAG] DAG visualization saved to '{full_filename}'")
            if display_in_notebook:
                display(Image(filename=full_filename))
        except Exception as e:
            print(f"[DAG] Error rendering DAG visualization: {e}")
