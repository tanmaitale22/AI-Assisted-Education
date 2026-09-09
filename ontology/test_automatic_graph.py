from daa_relationship_extractor import extract_relationships
from daa_graph_builder import build_daa_graph
from graph_validator import validate_knowledge


sample_text = """
Breadth First Search is a graph traversal algorithm.

BFS uses a Queue data structure to visit nodes level by level.

Depth First Search is another graph traversal algorithm.
DFS uses a Stack data structure.

Dijkstra's algorithm is used to solve the shortest path problem.

Dynamic Programming is an algorithmic technique that requires
optimal substructure and overlapping subproblems.
"""


# --------------------------------
# Step 1: Extract knowledge automatically
# --------------------------------

print("\n===== EXTRACTING KNOWLEDGE =====\n")

extracted_knowledge = extract_relationships(
    sample_text
)

print("\n===== VALIDATING KNOWLEDGE =====\n")

validated_knowledge = validate_knowledge(
    extracted_knowledge
)


# --------------------------------
# Step 2: Build ontology graph automatically
# --------------------------------

print("\n===== BUILDING KNOWLEDGE GRAPH =====\n")

nodes = build_daa_graph(
    validated_knowledge
)


# --------------------------------
# Step 3: Print created nodes
# --------------------------------

print("\n===== CREATED NODES =====\n")

for name, node in nodes.items():

    print(
        f"{name} → {node.__class__.__name__}"
    )


print("\n===== GRAPH BUILDING COMPLETE =====\n")