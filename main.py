# -*- coding: utf-8 -*-

# from IPython.display import Image, display # Import Image and display
from dag_traversal_utility import GeneralDAGData
from llm_dag_parameterizer import parameterize_dag

# from google.colab import userdata
# from google.colab import drive # Drive is not used in this context
# os.environ["GEMINI_API_KEY"] = userdata.get("GOOGLE_API_KEY")



def main():
    """#### Main Loops for Cachexia Arbitrary Bounds

    ##### Cachexia 1 disease informed - arbitrary bounds
    """

    # Cachexia1 DAG Data
    cachexia1_exp1 = GeneralDAGData(
        all_nodes={"A", "B", "F", "GC", "GM", "V"},
        raw_edges=[
            ("A", "GC"),
            ("B", "V"),
            ("F", "GM"),
            ("GC", "B"),
            ("GC", "V"),
            ("GM", "A"),
            ("GM", "B"),
            ("GM", "V"),
        ],
        node_descriptions={
            "A": "Adipate",
            "B": "Betaine",
            "F": "Fumarate",
            "GC": "Glucose",
            "GM": "Glutamine",
            "V": "Valine",
        },
        primary_domain_name="metabolic systems",
        secondary_domain_name="biochemistry",
        node_lower_bound={"A": 0, "B": 0, "F": 0, "GC": 0, "GM": 0, "V": 0},
        node_upper_bound={"A": 100, "B": 100, "F": 100, "GC": 100, "GM": 100, "V": 100},
        ground_truth_effect_sizes={
            ("GM", "A"): 0.0674,
            ("GC", "B"): 0.0181,
            ("GM", "B"): 0.1104,
            ("A", "GC"): 13.4753,
            ("F", "GM"): 10.7348,
            ("B", "V"): 0.1104,
            ("GC", "V"): 0.0068,
            ("GM", "V"): 0.0436,
        },
        phenomenon_overview="You are going to identify internal dynamics of a phenomena, Cachexia. Cachexia is a complicated metabolic syndrome related to underlying illness and characterized by muscle mass loss with or without fat mass loss that is often associated with anorexia, an inflammatory process, insulin resistance, and increased protein turnover.",
    )

    parameterize_dag(cachexia1_exp1, include_hard_constraints=True)

if __name__ == "__main__":
    main()