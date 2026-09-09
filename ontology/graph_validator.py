# --------------------------------
# Allowed node types
# --------------------------------

VALID_NODE_TYPES = {
    "Subject",
    "Topic",
    "Concept",
    "Algorithm",
    "DataStructure",
    "Problem",
    "Technique"
}


# --------------------------------
# Allowed relationship rules
#
# Format:
# relationship: (allowed source types, allowed target types)
# --------------------------------

RELATIONSHIP_RULES = {

    "uses": (
        {"Algorithm"},
        {"DataStructure"}
    ),

    "solves": (
        {"Algorithm"},
        {"Problem"}
    ),

    "requires": (
        {"Algorithm", "Technique"},
        {"Concept", "DataStructure"}
    ),

    "relatedTo": (
        VALID_NODE_TYPES,
        VALID_NODE_TYPES
    )
}


# --------------------------------
# Validate extracted knowledge
# --------------------------------

def validate_knowledge(extracted_knowledge):

    valid_nodes = []
    valid_relationships = []

    # --------------------------------
    # Step 1: Validate nodes
    # --------------------------------

    for node in extracted_knowledge["nodes"]:

        node_name = node.get("name")
        node_type = node.get("type")

        if not node_name or not node_type:
            print(
                f"Skipping invalid node: {node}"
            )
            continue

        if node_type not in VALID_NODE_TYPES:

            print(
                f"Invalid node type '{node_type}' "
                f"for node '{node_name}'. "
                f"Using Concept instead."
            )

            node_type = "Concept"

        valid_nodes.append({
            "name": node_name,
            "type": node_type
        })

    # --------------------------------
    # Create node lookup
    # --------------------------------

    node_types = {
        node["name"]: node["type"]
        for node in valid_nodes
    }

    # --------------------------------
    # Step 2: Validate relationships
    # --------------------------------

    for relationship in extracted_knowledge["relationships"]:

        source_name = relationship.get("source")
        relation_name = relationship.get("relation")
        target_name = relationship.get("target")

        # Check that nodes exist
        if (
            source_name not in node_types
            or target_name not in node_types
        ):

            print(
                f"Skipping relationship because "
                f"a node does not exist: "
                f"{relationship}"
            )

            continue

        # Check relationship exists
        if relation_name not in RELATIONSHIP_RULES:

            print(
                f"Skipping unknown relationship: "
                f"{relationship}"
            )

            continue

        source_type = node_types[source_name]
        target_type = node_types[target_name]

        allowed_sources, allowed_targets = (
            RELATIONSHIP_RULES[relation_name]
        )

        # Check source type
        if source_type not in allowed_sources:

            print(
                f"Invalid relationship skipped:\n"
                f"{source_name} ({source_type}) "
                f"-- {relation_name} --> "
                f"{target_name} ({target_type})"
            )

            continue

        # Check target type
        if target_type not in allowed_targets:

            print(
                f"Invalid relationship skipped:\n"
                f"{source_name} ({source_type}) "
                f"-- {relation_name} --> "
                f"{target_name} ({target_type})"
            )

            continue

        # Relationship is valid
        valid_relationships.append({
            "source": source_name,
            "relation": relation_name,
            "target": target_name
        })

    # --------------------------------
    # Return cleaned knowledge
    # --------------------------------

    return {
        "nodes": valid_nodes,
        "relationships": valid_relationships
    }