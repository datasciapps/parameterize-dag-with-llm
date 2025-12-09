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

        # Removed the alphabet limit as we're now using variable names directly

        self.prompt_template = self._generate_prompt_template()
        self.output_constraint_prompt = self._generate_output_constraint_prompt()

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

        prompt_template = (
            r"""Given the direct causes, you must propose a linear structural equation for the target variable $Y$. Do not use non-linear functions (e.g., exponential, sigmoid). The coefficients of the linear equation are continuous variables in space $\mathbb{R}$.
The target variable is $Y =$ {target_variable_formatted}.
The direct causes (Parents) are: {direct_causes_formatted}.
Propose the complete linear equation: $Y = \beta_0*1 + {equation_terms} + E_Y$. You *must* use the actual raw variable names (e.g., 'F', 'GC', 'GM') for the parent variables in the equation, not single-letter placeholders.

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
