"""
prompt_generator.py
Module defining the PromptPerNode class for generating prompts for nodes in a Directed Acyclic Graph (DAG).
"""

import graphviz


class PromptPerNode:
    def __init__(
        self,
        primary_domain_name: str,
        secondary_domain_name: str,
        target_variable_name: str,
        direct_parent_variables: list[str],
        node_descriptions: dict = None,
        node_lower_bounds: dict = None,
        node_upper_bounds: dict = None,
        include_constraints_in_prompt: bool = False,
        feedback_message: str = None,
        phenomenon_overview: str = None,
        dag=None,
        parameterized_equations: dict = None,
        include_parent_relationships: bool = True,
    ):
        self.primary_domain_name = primary_domain_name
        self.secondary_domain_name = secondary_domain_name
        self.target_variable_name = target_variable_name
        self.direct_parent_variables = direct_parent_variables
        self.node_descriptions = (
            node_descriptions if node_descriptions is not None else {}
        )
        self.node_lower_bounds = (
            node_lower_bounds if node_lower_bounds is not None else {}
        )
        self.node_upper_bounds = (
            node_upper_bounds if node_upper_bounds is not None else {}
        )
        self.include_constraints_in_prompt = include_constraints_in_prompt
        self.feedback_message = feedback_message  # New parameter for feedback
        self.phenomenon_overview = (
            phenomenon_overview  # New parameter for phenomenon overview
        )
        self.dag = dag  # DAG reference for detecting parent-parent relationships
        self.parameterized_equations = (
            parameterized_equations if parameterized_equations is not None else {}
        )  # Existing parameterization results
        self.include_parent_relationships = include_parent_relationships  # Toggle for parent-parent relationship inclusion

        # Removed the alphabet limit as we're now using variable names directly

        self.prompt_template = self._generate_prompt_template()
        self.output_constraint_prompt = self._generate_output_constraint_prompt()

    def _detect_parent_parent_edges(self) -> dict:
        """
        Detects direct edges between parents of the target node.
        Returns a dictionary where keys are parent names and values are lists of their parent children within the parent set.
        Example: {"A": ["B", "C"]} means A influences B and C (both parents of target).
        """
        if self.dag is None:
            return {}

        parent_parent_edges = {}
        parent_set = set(self.direct_parent_variables)

        # For each parent, check if it influences any other parent
        for parent_name in self.direct_parent_variables:
            if parent_name not in self.dag.nodes:
                continue

            parent_node = self.dag.nodes[parent_name]
            influenced_parents = []

            # Check which of its children are also in the parent set
            for child_node in parent_node.children:
                if child_node.name in parent_set and child_node.name != parent_name:
                    influenced_parents.append(child_node.name)

            if influenced_parents:
                parent_parent_edges[parent_name] = influenced_parents

        return parent_parent_edges

    def _generate_parent_relationships_section(self) -> str:
        """
        Generates a section describing the structural equations for parent-parent relationships.
        This helps the LLM understand how parents influence each other, preventing duplicate counting.
        """
        if not self.include_parent_relationships:
            return ""

        parent_parent_edges = self._detect_parent_parent_edges()

        if not parent_parent_edges:
            return ""

        section = "\n***STRUCTURAL DEPENDENCIES AMONG PARENTS***\nNote: Some parents have direct causal relationships with each other. To avoid double-counting contributions, consider the following:\n\n"

        for source_parent, target_parents in parent_parent_edges.items():
            source_desc = self.node_descriptions.get(source_parent, "")
            source_info = f"{source_parent}"
            if source_desc:
                source_info += f" ({source_desc})"

            for target_parent in target_parents:
                target_desc = self.node_descriptions.get(target_parent, "")
                target_info = f"{target_parent}"
                if target_desc:
                    target_info += f" ({target_desc})"

                section += f"- {source_info} → {target_info}: The effect of {source_parent} on {self.target_variable_name} may operate both directly AND indirectly through {target_parent}. Ensure your coefficients reflect this structure.\n"

        return section

    def _generate_parameterized_parent_equations_section(self) -> str:
        """
        Generates a section with existing parameterization results for parent-parent edges.
        This provides the LLM with the actual structural equations already established for parent relationships.
        """
        if not self.include_parent_relationships:
            return ""

        parent_parent_edges = self._detect_parent_parent_edges()

        if not parent_parent_edges or not self.parameterized_equations:
            return ""

        # Build section only if we have parameterizations for parent-parent edges
        equations_to_include = {}
        for source_parent, target_parents in parent_parent_edges.items():
            for target_parent in target_parents:
                if target_parent in self.parameterized_equations:
                    equations_to_include[target_parent] = self.parameterized_equations[
                        target_parent
                    ]

        if not equations_to_include:
            return ""

        section = "\n***EXISTING PARAMETERIZATIONS FOR PARENT RELATIONSHIPS***\nThe following parent relationships have already been parameterized. Use these as reference for understanding how parent variables depend on their own parents:\n\n"

        for node_name, equation in equations_to_include.items():
            node_desc = self.node_descriptions.get(node_name, "")
            node_info = f"{node_name}"
            if node_desc:
                node_info += f" ({node_desc})"

            section += f"{node_info}:\n  {equation}\n\n"

        return section

    def _generate_prompt_template(self) -> str:
        # Format target variable with description if available
        target_description = self.node_descriptions.get(self.target_variable_name, "")
        target_variable_formatted = f'"{self.target_variable_name}"'
        if target_description:
            target_variable_formatted += f': "{target_description}"'

        # Format direct parent variables with descriptions if available
        direct_causes_formatted_list = []
        for var in self.direct_parent_variables:
            parent_description = self.node_descriptions.get(var, "")
            parent_formatted = f'"{var}"'
            if parent_description:
                parent_formatted += f': "{parent_description}"'
            direct_causes_formatted_list.append(parent_formatted)
        direct_causes_formatted = ", ".join(direct_causes_formatted_list)

        # Generate Hard Constraints Text
        hard_constraints_text = ""
        if self.include_constraints_in_prompt:
            constraints_list = []
            # Check target variable
            t_lb = self.node_lower_bounds.get(self.target_variable_name)
            t_ub = self.node_upper_bounds.get(self.target_variable_name)
            if t_lb is not None and t_ub is not None:
                constraints_list.append(
                    f"- Variable {self.target_variable_name} is bounded within [{t_lb}, {t_ub}]."
                )

            # Check parent variables
            for var in self.direct_parent_variables:
                p_lb = self.node_lower_bounds.get(var)
                p_ub = self.node_upper_bounds.get(var)
                if p_lb is not None and p_ub is not None:
                    constraints_list.append(
                        f"- Variable {var} is bounded within [{p_lb}, {p_ub}]."
                    )

            if constraints_list:
                hard_constraints_text = (
                    "\nThe following hard constraints (value ranges) are known and must be respected:\n"
                    + "\n".join(constraints_list)
                    + "\n"
                )

        # Add feedback message if available
        feedback_text = ""
        if self.feedback_message:
            feedback_text = f"\n***PREVIOUS ATTEMPT FEEDBACK***\nYour previous proposal failed validation with the following issue: {self.feedback_message}. Please adjust your new proposal to resolve this issue and respect all given constraints.\n"

        # Generate parent relationships section
        parent_relationships_text = self._generate_parent_relationships_section()

        # Generate parameterized parent equations section
        parameterized_parent_equations_text = (
            self._generate_parameterized_parent_equations_section()
        )

        prompt_template = (
            r"""Given the direct causes, you must propose a linear structural equation for the target variable $Y$. Do not use non-linear functions (e.g., exponential, sigmoid). The coefficients of the linear equation are continuous variables in space $\mathbb{R}$.
The target variable is $Y =$ {target_variable_formatted}.
The direct causes (Parents) are: {direct_causes_formatted}.
{parent_relationships_text}{parameterized_parent_equations_text}Propose the complete linear equation: $Y = \beta_0*1 + {equation_terms} + E_Y$. You *must* use the actual raw variable names (e.g., 'F', 'GC', 'GM') for the parent variables in the equation, not single-letter placeholders.

{hard_constraints_text}
1.  Explicitly define the error term $E_Y$ (e.g., standard normal noise, $E_Y \sim N(0, \sigma^2)$).

2.  For each coefficient (\beta_0, {betas}), explain its {primary_domain_name_lower} plausibility, its expected sign (positive/negative), and justify your chosen magnitude (unit-effect).

Given the DAG for variable "{target_variable_name}", please provide a plausible linear parameterisation.

{feedback_text}""".replace("{target_variable_formatted}", target_variable_formatted)
            .replace("{direct_causes_formatted}", direct_causes_formatted)
            .replace("{primary_domain_name_lower}", self.primary_domain_name.lower())
            .replace("{hard_constraints_text}", hard_constraints_text)
            .replace("{target_variable_name}", self.target_variable_name)
            .replace("{feedback_text}", feedback_text)
            .replace("{parent_relationships_text}", parent_relationships_text)
            .replace("{parameterized_parent_equations_text}", parameterized_parent_equations_text)
        )

        # Now using actual variable names for equation terms and betas
        equation_terms = " + ".join(
            [
                f"\\beta_{var_name}*{var_name}"
                for var_name in self.direct_parent_variables
            ]
        )
        prompt_template = prompt_template.replace("{equation_terms}", equation_terms)

        betas = ", ".join(
            [f"\\beta_{var_name}" for var_name in self.direct_parent_variables]
        )
        prompt_template = prompt_template.replace("{betas}", betas)

        # Removed the variables replacement as it's no longer needed with direct variable names
        # variables = ", ".join([chr(ord('a') + i) for i in range(len(self.direct_parent_variables))])
        # prompt_template = prompt_template.replace("{variables}", variables)

        return prompt_template

    def _generate_output_constraint_prompt(self) -> str:
        plausibility_description = (
            f"{self.primary_domain_name.capitalize()} Plausibility"
        )
        return r"""Output format: Only respond in JSON format, with the following keys:
- plausibility: str ({plausibility_description})
- proposed_lin_str_eq: str (Proposed Linear Structural Equation, *do not use placeholder betas like \\beta_0, use concrete numerical values*)
""".format(plausibility_description=plausibility_description)

    def get_expert_profile_specification(self) -> str:
        _tentative_profile = f"You are a leading {self.primary_domain_name} researcher and an Structural Causal Model (SCM) expert in {self.secondary_domain_name}.\n"
        # Adding more details (in-context learning)
        if self.phenomenon_overview:
            _tentative_profile += f"{self.phenomenon_overview}\n"
        return _tentative_profile

    def get_full_prompt(self) -> str:
        return (
            self.get_expert_profile_specification()
            + self.prompt_template
            + self.output_constraint_prompt
        )

    def visualize_parent_child_relationship(self, effect_sizes: dict = None):
        """Generates and returns a Graphviz representation of the parent-child relationship.
        Args:
            effect_sizes (dict, optional): A dictionary where keys are parent variable names
                                           and values are their corresponding effect sizes. Defaults to None.
        """
        dot_string = "digraph G {\n"
        dot_string += "    rankdir=LR;\n"  # Left to right layout
        dot_string += f'    "Y: {self.target_variable_name}" [shape=box, style=filled, fillcolor=lightblue];\n'

        for parent in self.direct_parent_variables:
            if effect_sizes and parent in effect_sizes:
                label = f'label="{effect_sizes[parent]:e}";'  # Changed to scientific notation
                dot_string += (
                    f'    "{parent}" -> "Y: {self.target_variable_name}" [{label}];\n'
                )
            else:
                dot_string += f'    "{parent}" -> "Y: {self.target_variable_name}";\n'
        dot_string += "}\n"
        return graphviz.Source(dot_string)
