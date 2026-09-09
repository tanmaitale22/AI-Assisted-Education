from daa_relationship_extractor import extract_relationships


sample_text = """
Breadth First Search is a graph traversal algorithm.

BFS uses a Queue data structure to visit nodes level by level.

Depth First Search is another graph traversal algorithm.
DFS uses a Stack data structure.

Dijkstra's algorithm is used to solve the shortest path problem.

Dynamic Programming is an algorithmic technique that requires
optimal substructure and overlapping subproblems.
"""


result = extract_relationships(sample_text)


print("\n===== EXTRACTED KNOWLEDGE =====\n")

print("NODES:\n")

for node in result["nodes"]:
    print(
        f"{node['name']} → {node['type']}"
    )


print("\nRELATIONSHIPS:\n")

for relationship in result["relationships"]:
    print(
        f"{relationship['source']} "
        f"-- {relationship['relation']} --> "
        f"{relationship['target']}"
    )