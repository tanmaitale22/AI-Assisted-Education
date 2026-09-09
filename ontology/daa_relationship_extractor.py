import json
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from gemini_service import ask_gemini

def extract_relationships(text):

    prompt = f"""
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

Allowed relationships:

- hasTopic
- hasSubtopic
- uses
- solves
- requires
- relatedTo

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

2. Do not invent concepts or relationships.

3. Every relationship source and target must exist in nodes.

4. Use the most appropriate allowed node type.

5. Use the most appropriate allowed relationship.

6. Avoid duplicate nodes.

7. Focus only on academically meaningful DAA concepts.

8. Relationship meanings must follow these rules:

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

   - relatedTo:
     Use this only when two concepts are academically
     related but no more specific relationship applies.

   - hasTopic:
     A Subject can have a Topic.

   - hasSubtopic:
     A Topic can have a Concept or subtopic.

9. A broad concept such as "Graph Traversal" should normally
   be classified as a Concept or Topic, not as a Problem.

10. Before assigning a relationship, check whether the
    relationship is logically meaningful based on the node types.

11. Prefer a more specific relationship over "relatedTo"
    when the relationship is clearly known.

12. If no logically valid relationship can be identified,
    do not create one.

13. Return ONLY JSON. Do not include explanations or markdown.

STUDY MATERIAL:

{text}
"""

    response = ask_gemini(prompt, "")

    response = response.strip()

    # Remove markdown if Gemini returns it
    if response.startswith("```"):
        response = response.replace(
            "```json",
            ""
        )
        response = response.replace(
            "```",
            ""
        )
        response = response.strip()

    return json.loads(response)