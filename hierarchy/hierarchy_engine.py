import json

from gemini_service import ask_gemini
from hierarchy.hierarchy_store import HierarchyStore
from rag.chunker import chunk_text


class HierarchyEngine:

    def __init__(self):
        self.store = HierarchyStore()

    def generate_hierarchy(self, text, filename, rag_chunks):

        # --------------------------------
        # Step 1: Generate hierarchy
        # --------------------------------

        prompt = f"""
You are an educational content structure analyzer.

Analyze the following study material and create a hierarchical structure.

Return ONLY valid JSON in this exact format:

{{
    "title": "Main title",
    "topics": [
        {{
            "name": "Topic name",
            "subtopics": [
                "Subtopic 1",
                "Subtopic 2"
            ]
        }}
    ]
}}

Rules:
- Identify the main title.
- Identify meaningful academic topics.
- Identify important subtopics.
- Do not invent information.
- Ignore sections such as "keywords", "test questions",
  "references", or "self assessment" unless they are actual
  academic topics.
- Keep the hierarchy concise.
- Return ONLY JSON.

Filename:
{filename}

Study material:
{text}
"""

        response = ask_gemini(prompt, "")

        response = response.strip()

        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        hierarchy = json.loads(response)

        # --------------------------------
        # Step 2: Create topic-aware sections
        # --------------------------------

        sections_prompt = f"""
You are an educational content organizer.

You are given a study document and its academic hierarchy.

Your task is to divide the document into meaningful
topic-aware sections.

Each section must belong to exactly ONE subtopic.

Return ONLY valid JSON in this exact format:

{{
    "sections": [
        {{
            "topic": "Topic name",
            "subtopic": "Subtopic name",
            "content": "Content belonging to this subtopic"
        }}
    ]
}}

Rules:
- Use ONLY topic and subtopic names from the hierarchy.
- Do NOT create new topics or subtopics.
- Every section must contain meaningful educational content.
- Do not mix unrelated topics in the same section.
- Keep related explanations together.
- Preserve the important information from the original document.
- Do not summarize or remove important technical details.
- Ignore keywords, references, test questions and self-assessment
  sections unless they contain actual academic explanation.
- A topic may contain multiple sections.
- A subtopic may contain multiple sections.
- Return ONLY JSON.

HIERARCHY:

{json.dumps(hierarchy, indent=2)}

STUDY MATERIAL:

{text}
"""

        sections_response = ask_gemini(
            sections_prompt,
            ""
        )

        sections_response = sections_response.strip()

        if sections_response.startswith("```"):
            sections_response = sections_response.replace(
                "```json", ""
            )
            sections_response = sections_response.replace(
                "```", ""
            )
            sections_response = sections_response.strip()

        sections_data = json.loads(sections_response)

        print("\n===== TOPIC-AWARE SECTIONS =====")

        for section in sections_data["sections"]:
            print(
                f"\nTOPIC: {section['topic']}"
                f"\nSUBTOPIC: {section['subtopic']}"
                f"\nCONTENT: {section['content'][:300]}"
            )

        print("\n===============================\n")

        # --------------------------------
        # Step 3: Create chunks from sections
        # --------------------------------

        final_chunks = []

        chunk_index = 0

        for section in sections_data["sections"]:

            topic = section["topic"]
            subtopic = section["subtopic"]
            content = section["content"]

            # Split very large sections into smaller chunks
            section_chunks = chunk_text(
                content,
                chunk_size=1000,
                overlap=200
            )

            for section_chunk in section_chunks:

                final_chunks.append({
                    "index": chunk_index,
                    "content": section_chunk,
                    "topic": topic,
                    "subtopic": subtopic
                })

                chunk_index += 1

        # --------------------------------
        # Step 4: Save hierarchy + chunks
        # --------------------------------

        self.store.save_hierarchy(
            filename,
            hierarchy["title"],
            hierarchy["topics"],
            final_chunks
        )

        return hierarchy, final_chunks