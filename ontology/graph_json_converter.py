import os
from owlready2 import get_ontology


def convert_graph_to_json():

    # --------------------------------
    # Locate OWL file
    # --------------------------------

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    owl_path = os.path.join(
        current_dir,
        "daa_knowledge_graph.owl"
    )

    # --------------------------------
    # Load ontology
    # --------------------------------

    onto = get_ontology(owl_path).load()

    nodes = []
    edges = []

    # --------------------------------
    # Extract nodes
    # --------------------------------

    for individual in onto.individuals():

        node_id = individual.name

        # Get ontology class
        node_type = "Concept"

        if individual.is_a:
            node_type = individual.is_a[0].name

        nodes.append({
            "data": {
                "id": node_id,
                "label": node_id.replace("_", " "),
                "type": node_type
            }
        })

    # --------------------------------
    # Extract relationships
    # --------------------------------

    edge_index = 0

    for individual in onto.individuals():

        source_id = individual.name

        for property in individual.get_properties():

            # Get property values
            for target in property[individual]:

                # Ignore non-ontology relationships
                if not hasattr(target, "name"):
                    continue

                edge_id = (
                    f"edge_{edge_index}"
                )

                edges.append({
                    "data": {
                        "id": edge_id,
                        "source": source_id,
                        "target": target.name,
                        "label": property.name
                    }
                })

                edge_index += 1

    return {
        "nodes": nodes,
        "edges": edges
    }


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    import json

    graph_data = convert_graph_to_json()

    print(
        json.dumps(
            graph_data,
            indent=4
        )
    )