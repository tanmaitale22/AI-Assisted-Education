from owlready2 import get_ontology
from pathlib import Path


# --------------------------------
# Load generated knowledge graph
# --------------------------------

graph_path = (
    Path(__file__).parent /
    "daa_knowledge_graph.owl"
)

onto = get_ontology(
    graph_path.as_uri()
).load()


# --------------------------------
# Print nodes
# --------------------------------

print("\n===== NODES =====\n")

for individual in onto.individuals():

    node_type = (
        individual.is_a[0].name
        if individual.is_a
        else "Unknown"
    )

    print(
        f"{individual.name} → {node_type}"
    )


# --------------------------------
# Print relationships
# --------------------------------

print("\n===== RELATIONSHIPS =====\n")

for individual in onto.individuals():

    for property in onto.object_properties():

        values = property[individual]

        for value in values:

            # Some values may not be ontology individuals
            if hasattr(value, "name"):

                print(
                    f"{individual.name} "
                    f"-- {property.name} --> "
                    f"{value.name}"
                )