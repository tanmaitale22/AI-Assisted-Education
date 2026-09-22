from pathlib import Path
from owlready2 import get_ontology

from ontology.daa_ontology import (
    Subject,
    Topic,
    Concept,
    Algorithm,
    DataStructure,
    Problem,
    Technique,
    hasTopic,
    hasSubtopic,
    belongsTo,
    uses,
    solves,
    requires,
    relatedTo
)

# --------------------------------
# Paths
# --------------------------------

CURRENT_DIRECTORY = Path(__file__).parent

GRAPH_PATH = (
    CURRENT_DIRECTORY
    / "daa_knowledge_graph.owl"
)


# --------------------------------
# Relationship type mapping
# --------------------------------

RELATION_TYPES = {
    "hasTopic": hasTopic,
    "hasSubtopic": hasSubtopic,
    "belongsTo": belongsTo,
    "uses": uses,
    "solves": solves,
    "requires": requires,
    "relatedTo": relatedTo
}

# --------------------------------
# Create safe OWL identifier
# --------------------------------

def create_node_name(name):

    return (
        name.strip()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("'", "")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
    )


# --------------------------------
# Load knowledge graph
# --------------------------------

def load_knowledge_graph():

    if GRAPH_PATH.exists():

        print(
            "\nLoading existing knowledge graph..."
        )

        return get_ontology(
            GRAPH_PATH.as_uri()
        ).load()

    print(
        "\nNo existing knowledge graph found."
    )

    print(
        "Creating a fresh knowledge graph..."
    )

    from ontology.daa_ontology import onto

    return onto


# --------------------------------
# Find existing node
# --------------------------------

def find_existing_node(graph, node_name):

    safe_name = create_node_name(
        node_name
    )

    for individual in graph.individuals():

        if individual.name == safe_name:

            return individual

    return None


# --------------------------------
# Build or update knowledge graph
# --------------------------------

def build_daa_graph(extracted_knowledge):

    # Load the EXISTING knowledge graph
    graph = load_knowledge_graph()
    
    NODE_TYPES = {
        "Subject": graph.Subject,
        "Topic": graph.Topic,
        "Concept": graph.Concept,
        "Algorithm": graph.Algorithm,
        "DataStructure": graph.DataStructure,
        "Problem": graph.Problem,
        "Technique": graph.Technique
    }

    nodes = {}

    new_nodes = 0
    existing_nodes = 0
    new_relationships = 0

    # --------------------------------
    # Create or reuse nodes
    # --------------------------------

    for node in extracted_knowledge["nodes"]:

        node_name = node["name"]
        node_type = node["type"]

        existing_node = find_existing_node(
            graph,
            node_name
        )

        if existing_node:

            ontology_node = existing_node

            existing_nodes += 1

            print(
                f"Reusing existing node: "
                f"{node_name}"
            )

        else:

            ontology_class = NODE_TYPES.get(
                node_type,
                Concept
            )

            safe_name = create_node_name(
                node_name
            )

            # Create the individual
            # inside the loaded graph context
            with graph:

                ontology_node = ontology_class(
                    safe_name
                )

            new_nodes += 1

            print(
                f"Created new node: "
                f"{node_name}"
            )

        nodes[node_name] = ontology_node


    # --------------------------------
    # Resolve nodes
    # --------------------------------

    def resolve_node(name):

        if name in nodes:

            return nodes[name]

        return find_existing_node(
            graph,
            name
        )


    # --------------------------------
    # Create relationships
    # --------------------------------

    for relationship in extracted_knowledge["relationships"]:

        source_name = relationship["source"]
        relation_name = relationship["relation"]
        target_name = relationship["target"]

        source = resolve_node(source_name)
        target = resolve_node(target_name)

        if source is None or target is None:

            print(
                f"Skipping invalid relationship: "
                f"{source_name} -- "
                f"{relation_name} --> "
                f"{target_name}"
            )

            continue

        relation_property = RELATION_TYPES.get(
            relation_name
        )

        if relation_property is None:

            print(
                f"Unknown relationship: "
                f"{relation_name}"
            )

            continue


        # Prevent duplicate relationships

        if target not in relation_property[source]:

            relation_property[source].append(
                target
            )

            new_relationships += 1

            print(
                f"Added relationship: "
                f"{source_name} -- "
                f"{relation_name} --> "
                f"{target_name}"
            )

        else:

            print(
                f"Relationship already exists: "
                f"{source_name} -- "
                f"{relation_name} --> "
                f"{target_name}"
            )


    # --------------------------------
    # Save the SAME loaded graph
    # --------------------------------

    graph.save(
        file=str(GRAPH_PATH),
        format="rdfxml"
    )


    print(
        "\n===== KNOWLEDGE GRAPH UPDATED =====\n"
    )

    print(
        f"New nodes: {new_nodes}"
    )

    print(
        f"Existing nodes reused: "
        f"{existing_nodes}"
    )

    print(
        f"New relationships added: "
        f"{new_relationships}"
    )

    print(
        f"\nSaved at: {GRAPH_PATH}"
    )

    return nodes