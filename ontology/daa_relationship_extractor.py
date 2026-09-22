import json
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )\
    )
)

from gemini_service import ask_gemini


# ---------------------------------------------------------------------------
# PROMPT BUILDERS
# ---------------------------------------------------------------------------

def build_extraction_prompt(text):
    return f"""
    You are analyzing study material for the subject
    Design and Analysis of Algorithms (DAA).

    Extract important academic concepts and the semantic
    relationships between them.

    Return ONLY valid JSON in this exact format:

    {{
        "nodes": [
            {{
                "name": "Concept name",
                "type": "Algorithm"
            }}
        ],
        "relationships": [
            {{
                "source": "Source concept",
                "relation": "uses",
                "target": "Target concept"
            }}
        ]
    }}

    Allowed node types:

    - Subject
    - Topic
    - Concept
    - Algorithm
    - DataStructure
    - Problem
    - Technique

    Allowed relationships: hasTopic, hasSubtopic, uses, solves,
    requires, relatedTo.

    Relationship type constraints:

    - hasTopic: Subject → Topic
    - hasSubtopic: Topic → Concept/Algorithm/DataStructure/Problem/Technique
    - uses: Algorithm/Technique → DataStructure/Concept/Technique
    - solves: Algorithm → Problem
    - requires: Algorithm/Technique → Concept/DataStructure
    - relatedTo: non-Topic node → non-Topic node

    NODE TYPE DEFINITIONS:

    Subject:
    The overall academic subject.

    Topic:
    A broad major area within the subject.

    Concept:
    A theoretical idea, principle, property, or general process.

    Algorithm:
    A step-by-step computational method used to solve a problem.

    DataStructure:
    A method of organizing and storing data.

    Problem:
    A specific computational problem that requires a solution.

    Technique:
    A general problem-solving approach or strategy.

    CLASSIFICATION RULES:

    - Do not classify a broad area such as "Graph Traversal"
    as a Problem unless the text explicitly presents it
    as a problem to be solved.

    - Use Concept for theoretical ideas or general areas
    that do not clearly fit another category.

    - Use Problem only for actual computational problems
    such as "Shortest Path Problem" or "Knapsack Problem".

    - Prefer Concept when uncertain.

    Rules:

    1. Extract only concepts that actually appear in the study material.

    2. Every relationship source and target must exist in nodes.

    3. Use the most appropriate allowed node type.

    4. Use the most appropriate allowed relationship.

    5. Avoid duplicate nodes and duplicate relationships.

    6. Focus only on academically meaningful DAA concepts.

    7. Relationship meanings must follow these rules:

        - uses:
            An Algorithm or Technique uses a DataStructure or Concept.

            Example:
            Breadth First Search -- uses --> Queue

        - solves:
            An Algorithm solves a specific computational Problem.

            Example:
            Dijkstra's Algorithm -- solves --> Shortest Path Problem

            Do NOT use "solves" for broad concepts such as
            Graph Traversal.

        - requires:
            An Algorithm or Technique requires a Concept,
            property, or prerequisite.

            Example:
            Dynamic Programming -- requires --> Optimal Substructure

        - hasSubtopic:
            Use when the source node is a Topic and the target is a
            Concept, Algorithm, DataStructure, Problem, or Technique
            that is discussed as part of that Topic.

            Examples:
            Analysis of Algorithms -- hasSubtopic --> Time Complexity
            Sorting -- hasSubtopic --> Merge Sort
            Graph Algorithms -- hasSubtopic --> Breadth-First Search
            Computational Complexity -- hasSubtopic --> P vs NP

            IMPORTANT:
            If the source is a Topic and the target is a node that is
            part of, discussed under, or taught within that Topic,
            ALWAYS prefer hasSubtopic.

            Do NOT use relatedTo for Topic → Concept,
            Topic → Algorithm, Topic → DataStructure,
            Topic → Problem, or Topic → Technique relationships.

        - relatedTo:
            Use only for meaningful associations between non-Topic
            knowledge nodes when the relationship does not fit
            uses, solves, requires, or hasSubtopic.

            The source and target of relatedTo must NOT be a Topic.

            Examples:
            Divide and Conquer -- relatedTo --> Merge Sort
            Greedy Method -- relatedTo --> Fractional Knapsack Problem
            Dynamic Programming -- relatedTo --> 0/1 Knapsack Problem
            Backtracking -- relatedTo --> N-Queens Problem

    8. A relationship must be grounded in the study material —
       either stated explicitly, or the node is clearly discussed
       within the context of another node (same passage, same
       heading/topic). Do not invent relationships from general
       CS knowledge that don't appear in this text.

    9. Before assigning a relationship, check whether it is
       logically meaningful based on the node types involved.

    10. Prefer a more specific relationship over "relatedTo"
        when the relationship is clearly known.

    11. Try to connect every node to at least one other node.
        Do not leave a node with zero relationships if the study
        material gives any context that links it to something else.
    
    RELATIONSHIP COMPLETENESS:

        After identifying all nodes, perform a second pass over the
        study material specifically for relationships.

        For EVERY extracted node, check whether the study material
        provides at least one meaningful relationship involving that node.

        In particular, look for relationships between:

        - Topics and their algorithms or concepts
        - Algorithms and the techniques they use
        - Algorithms and the problems they solve
        - Algorithms and required concepts or data structures
        - Techniques and their required concepts
        - Problems and algorithms that solve them
        - Algorithms that belong to or are discussed under a topic

        Examples:

        Sorting -- hasSubtopic --> Merge Sort

        Divide and Conquer -- hasSubtopic --> Merge Sort

        Greedy Method -- requires --> Greedy-Choice Property

        Dynamic Programming -- requires --> Optimal Substructure

        Kruskal's Algorithm -- uses --> Disjoint Set Union

        Kruskal's Algorithm -- solves --> Minimum Spanning Tree Problem

        Backtracking -- hasSubtopic --> N-Queens Problem

        IMPORTANT:

        Do not create relationships merely because they are commonly
        associated in computer science.

        A relationship must be supported by the study material.

        However, if the study material clearly discusses two extracted
        nodes together or establishes that one is used, required,
        solved, or belongs to another, capture that relationship.

        Do not leave a node isolated if the study material explicitly
        provides enough information to connect it to another extracted
        node.

        Before returning the JSON, verify:

        1. Every relationship has valid source and target nodes.
        2. Every relationship follows the allowed relationship rules.
        3. Every extracted node has been checked for possible
        relationships.
        4. No relationship is invented.
        5. Duplicate relationships are removed.

    STUDY MATERIAL:

    {text}
    """


def build_repair_prompt(text, isolated_names, all_node_names):
    """
    Second-pass prompt: asks Gemini to connect ONLY the nodes that
    ended up with zero relationships in the first pass. This is a
    much smaller, more focused task than extracting the whole graph
    at once, so the model is far more likely to actually find a
    connection for each one instead of skipping it.
    """
    isolated_list = "\n".join(f"- {n}" for n in isolated_names)
    all_list = "\n".join(f"- {n}" for n in all_node_names)

    return f"""
    You previously extracted a knowledge graph from DAA study
    material. The following nodes ended up with NO relationships
    at all, which should not happen if the text gives any context
    connecting them to something else:

    ISOLATED NODES:
    {isolated_list}

    Here is the FULL list of nodes already in the graph (you may
    connect an isolated node to any of these, including other
    isolated nodes if that's what the text supports):

    ALL NODES:
    {all_list}

    Allowed relationships: hasTopic, hasSubtopic, uses, solves,
    requires, relatedTo.

    For EACH isolated node above, re-read the study material below
    and find at least one relationship connecting it to another
    node in ALL NODES. Use this priority:

      1. A specific relation (uses / solves / requires / hasSubtopic)
         if the text clearly supports it.
      2. If the isolated node is a Concept, Algorithm, DataStructure,
        Problem, or Technique and the text clearly places it under a
        Topic, use:

            Topic -- hasSubtopic --> isolated nod
      3. Otherwise, use relatedTo only when BOTH source and target
        are non-Topic nodes and the relationship is explicitly
        supported by the study material.

    Return ONLY valid JSON, no markdown, no explanation, in this
    exact format:

    {{
        "relationships": [
            {{
                "source": "Source concept",
                "relation": "relatedTo",
                "target": "Target concept"
            }}
        ]
    }}

    Every source or target you output MUST be a name that appears
    in ALL NODES above (either the isolated node itself or another
    existing node). Do not invent new node names.

    STUDY MATERIAL:

    {text}
    """


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _call_gemini_json(prompt):
    response = ask_gemini(prompt, "")
    response = response.strip()

    if response.startswith("```"):
        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.strip()

    return json.loads(response)


def _find_isolated_nodes(nodes, relationships):
    connected = set()
    for rel in relationships:
        connected.add(rel["source"])
        connected.add(rel["target"])

    return [n["name"] for n in nodes if n["name"] not in connected]


def _dedupe_relationships(relationships):
    seen = set()
    deduped = []
    for rel in relationships:
        key = (rel["source"], rel["relation"], rel["target"])
        if key not in seen:
            seen.add(key)
            deduped.append(rel)
    return deduped


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def extract_relationships(text, max_repair_passes=2):
    # --- Pass 1: initial extraction ---
    prompt = build_extraction_prompt(text)
    result = _call_gemini_json(prompt)

    print("\n========== GEMINI GRAPH EXTRACTION (PASS 1) ==========")
    print(json.dumps(result, indent=2))
    print("=======================================================\n")

    nodes = result.get("nodes", [])
    relationships = result.get("relationships", [])

    node_names = {n["name"] for n in nodes}
    # keep only relationships whose endpoints actually exist
    relationships = [
        r for r in relationships
        if r["source"] in node_names and r["target"] in node_names
    ]

    # --- Repair passes: find isolated nodes and try to connect them ---
    for attempt in range(1, max_repair_passes + 1):
        isolated = _find_isolated_nodes(nodes, relationships)

        if not isolated:
            break

        print(f"---- Repair pass {attempt}: {len(isolated)} isolated node(s) ----")
        print(isolated)

        repair_prompt = build_repair_prompt(
            text,
            isolated_names=isolated,
            all_node_names=sorted(node_names),
        )
        repair_result = _call_gemini_json(repair_prompt)

        new_rels = repair_result.get("relationships", [])
        # only keep relationships whose endpoints are real nodes
        new_rels = [
            r for r in new_rels
            if r.get("source") in node_names and r.get("target") in node_names
        ]

        if not new_rels:
            # model couldn't find anything new this round; stop looping
            break

        relationships.extend(new_rels)
        relationships = _dedupe_relationships(relationships)

    # --- Final report ---
    still_isolated = _find_isolated_nodes(nodes, relationships)
    if still_isolated:
        print("\n[WARNING] Nodes still without any relationship after repair passes:")
        print(still_isolated)
        print("These are likely mentioned in the source text with no surrounding")
        print("context at all — consider reviewing the source material for them.\n")

    return {
        "nodes": nodes,
        "relationships": relationships,
    }