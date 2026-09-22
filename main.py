# import os
# import shutil
# import subprocess
# import sys
# import re
# from difflib import SequenceMatcher
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pathlib import Path
# from pydantic import BaseModel
# from gemini_service import ask_ai
# from processors.pdf_processor import extract_pdf_text
# from rag.rag_engine import RAGEngine
# from memory.memory_engine import MemoryEngine
# from hierarchy.hierarchy_engine import HierarchyEngine
# from typing import Optional
# from ontology.graph_json_converter import convert_graph_to_json
# from ontology.daa_relationship_extractor import extract_relationships
# from ontology.graph_validator import validate_knowledge
# from ontology.daa_graph_builder import build_daa_graph
# from urllib.parse import unquote
# # from processors.video_processor import transcribe_video

# app = FastAPI(title="AI Education System")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# rag_engine = RAGEngine()
# memory_engine = MemoryEngine()
# hierarchy_engine = HierarchyEngine()

# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)


# @app.get("/")
# def home():
#     return {
#         "message": "AI Education Backend is running"
#     }

# @app.post("/upload")
# async def upload_files(files: list[UploadFile] = File(...)):

#     uploaded_files = []

#     for file in files:

#         filename = file.filename

#         if not filename:
#             continue

#         extension = Path(filename).suffix.lower()

#         if extension not in [".pdf", ".pptx"]:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Unsupported file type: {filename}"
#             )

#         file_path = UPLOAD_DIR / filename

#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # --------------------------------
#         # Extract text
#         # --------------------------------

#         if extension == ".pdf":
#             text = extract_pdf_text(file_path)
#         else:
#             text = extract_ppt_text(file_path)

#         # --------------------------------
#         # Generate topic-aware chunks
#         # --------------------------------

#         hierarchy, topic_chunks = hierarchy_engine.generate_hierarchy(
#             text,
#             filename,
#             []
#         )

#         # --------------------------------
#         # Store topic-aware chunks in FAISS
#         # --------------------------------

#         rag_engine.add_document(topic_chunks)

#         # --------------------------------
#         # ONTOLOGY KNOWLEDGE EXTRACTION
#         # --------------------------------

#         extracted_knowledge = extract_relationships(text)

#         validated_knowledge = validate_knowledge(
#             extracted_knowledge
#         )

#         build_daa_graph(
#             validated_knowledge
#         )

#         # --------------------------------
#         # Response
#         # --------------------------------

#         uploaded_files.append({
#             "filename": filename,
#             "characters": len(text),
#             "chunks": topic_chunks,
#             "hierarchy": hierarchy
#         })

#     return {
#         "files_uploaded": len(uploaded_files),
#         "documents": uploaded_files
#     }

# @app.post("/upload-video")
# async def upload_video(file: UploadFile = File(...)):

#     # Check video type
#     if not file.content_type or not file.content_type.startswith("video/"):
#         raise HTTPException(
#             status_code=400,
#             detail="Please upload a valid video file."
#         )

#     filename = file.filename

#     if not filename:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid filename."
#         )

#     # Save video
#     video_path = UPLOAD_DIR / filename

#     with open(video_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # --------------------------------
#     # Run Whisper in a separate process
#     # --------------------------------

#     try:

#         result = subprocess.run(
#             [
#                 sys.executable,
#                 "processors/transcribe_worker.py",
#                 str(video_path)
#             ],
#             capture_output=True,
#             text=True,
#             check=True
#         )

#         transcript = result.stdout.strip()

#     except subprocess.CalledProcessError as e:

#         print("Whisper worker error:")
#         print(e.stderr)

#         raise HTTPException(
#             status_code=500,
#             detail="Video transcription failed."
#         )

#     # --------------------------------
#     # Generate hierarchy
#     # --------------------------------

#     hierarchy, topic_chunks = hierarchy_engine.generate_hierarchy(
#         transcript,
#         filename,
#         []
#     )

#     # --------------------------------
#     # Add to RAG
#     # --------------------------------

#     rag_engine.add_document(topic_chunks)

#     return {
#         "filename": filename,
#         "characters": len(transcript),
#         "transcript": transcript,
#         "chunks": topic_chunks,
#         "hierarchy": hierarchy
#     }


# @app.get("/hierarchy")
# def get_hierarchy():
#     return hierarchy_engine.store.get_hierarchy()

# @app.get("/knowledge-graph")
# def get_knowledge_graph():
#     return convert_graph_to_json()

# @app.get("/knowledge-graph/node/{node_name}")
# def get_node_context(node_name: str):

#     node_name = unquote(node_name)

#     matching_chunks = []

#     for chunk in rag_engine.vector_store.chunks:

#         content = chunk.get("content", "")
#         topic = chunk.get("topic", "")
#         subtopic = chunk.get("subtopic", "")

#         # Prefer exact topic/subtopic matches
#         if (
#             node_name.lower() == topic.lower()
#             or node_name.lower() == subtopic.lower()
#         ):
#             matching_chunks.append(chunk)

#     # If no exact topic/subtopic match,
#     # search for the node name inside chunk content
#     if not matching_chunks:

#         for chunk in rag_engine.vector_store.chunks:

#             content = chunk.get("content", "")

#             if node_name.lower() in content.lower():
#                 matching_chunks.append(chunk)

#     # Limit the amount of material returned
#     unique_chunks = []

#     for chunk in matching_chunks:

#         content = chunk.get("content", "")

#         normalized_content = re.sub(
#             r"\s+",
#             " ",
#             content
#         ).strip().lower()

#         if not normalized_content:
#             continue

#         is_duplicate = False

#         for existing_chunk in unique_chunks:

#             existing_content = re.sub(
#                 r"\s+",
#                 " ",
#                 existing_chunk.get("content", "")
#             ).strip().lower()

#             similarity = SequenceMatcher(
#                 None,
#                 normalized_content,
#                 existing_content
#             ).ratio()

#             if similarity >= 0.85:
#                 is_duplicate = True
#                 break

#         if not is_duplicate:
#             unique_chunks.append(chunk)

#         if len(unique_chunks) == 5:
#             break

#     matching_chunks = unique_chunks

#     return {
#         "node": node_name,
#         "chunks": matching_chunks
#     }


# class Question(BaseModel):
#     question: str
#     topic: Optional[str] = None
#     subtopic: Optional[str] = None
#     document: Optional[str] = None
    
# def is_memory_question(question: str):
#     memory_phrases = [
#         "what did we just discuss",
#         "what did we just talk about",
#         "what were we just discussing",
#         "what did we discuss",
#         "what did we talk about",
#         "remind me what we discussed",
#         "remind me what we talked about",
#         "what was my last question",
#         "what did i just ask",
#         "what did i ask just now",
#     ]

#     question_lower = question.lower()

#     return any(
#         phrase in question_lower
#         for phrase in memory_phrases
#     )


# @app.post("/ask")
# def ask_question(request: Question):

#     memory_only = is_memory_question(request.question)

#     # 1. Retrieve relevant study material
#     if memory_only:
#         relevant_chunks = []

#     elif request.topic and request.subtopic:
#         # Subtopic-specific AI
#         relevant_chunks = rag_engine.retrieve(
#             request.question,
#             top_k=3,
#             topic=request.topic,
#             subtopic=request.subtopic
#         )

#     else:
#         # Global AI — search across all study material
#         relevant_chunks = rag_engine.retrieve(
#             request.question,
#             top_k=5
#         )

#     # 2. Create RAG context
#     if memory_only:
#         context = """
#         The student is asking about their conversation history.

#         Do not use the study material to answer this question.
#         """

#     elif request.topic and request.subtopic:
#         context = f"""
#         Current Study Context:
#         Document: {request.document}
#         Topic: {request.topic}
#         Subtopic: {request.subtopic}

#         Relevant Study Material:
#         """

#     else:
#         context = """
#         The student is asking a general question about their uploaded study material.

#         Relevant Study Material:
#         """

#     for chunk in relevant_chunks:
#         context += f"""
#         Topic: {chunk['topic']}
#         Subtopic: {chunk['subtopic']}
#         Content: {chunk['content']}
#         """

#     # 3. Retrieve student's previous interactions
#     memories = memory_engine.get_relevant_memories(
#         request.question,
#         top_k=5
#     )

#     memory_context = ""

#     if memories:
#         memory_context = """
#         CONVERSATION HISTORY

#         The interactions below are listed from OLDEST to NEWEST.
#         Use their order when answering questions about what happened
#         before, after, earlier, later, or most recently.

#         """

#         for i, memory in enumerate(memories, start=1):
#                     memory_context += f"""
#         Interaction {i}:
#         User: {memory['question']}
#         AI: {memory['answer']}

#         """

#     else:
#         memory_context = """
#         No previous conversation history is available.
#         """

#     # 4. Build the contextual question for Gemini
#     if memory_only:

#         contextual_question = f"""
#         The student is asking about their conversation history.

#         Use the CONVERSATION HISTORY provided to answer the question.

#         Important instructions:
#         - Treat the conversation history as chronological.
#         - The interactions are ordered from OLDEST to NEWEST.
#         - "Most recent" means the LAST interaction.
#         - "Before" means an earlier interaction.
#         - "After" means a later interaction.
#         - Do not use the uploaded study material to answer this question.
#         - Do not invent conversations that are not present in the history.

#         Student's question:
#         {request.question}
#         """

#     elif request.topic and request.subtopic:

#         contextual_question = f"""
#         The student is currently studying:

#         Document: {request.document}
#         Topic: {request.topic}
#         Subtopic: {request.subtopic}

#         Answer the student's question using the provided study material.

#         Student's question:
#         {request.question}
#         """

#     else:

#         contextual_question = f"""
#         The student is asking a general question about their uploaded study material.

#         Answer the student's question using the provided study material.

#         Student's question:
#         {request.question}
#         """

#     # 5. Send study material + conversation memory to Gemini
#     answer = ask_ai(
#         contextual_question,
#         context + "\n\n" + memory_context
#     )

#     # 6. Save the new interaction
#     memory_engine.remember(
#         request.question,
#         answer,
#         request.document,
#         request.topic,
#         request.subtopic
#     )

#     return {
#         "question": request.question,
#         "retrieved_chunks": relevant_chunks,
#         "answer": answer,
#         "memory_used": memories
#     }

import os
import shutil
import subprocess
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from gemini_service import ask_ai
from processors.pdf_processor import extract_pdf_text
from rag.rag_engine import RAGEngine
from memory.memory_engine import MemoryEngine
from hierarchy.hierarchy_engine import HierarchyEngine
from typing import Optional
from ontology.graph_json_converter import convert_graph_to_json
from ontology.daa_relationship_extractor import extract_relationships
from ontology.graph_validator import validate_knowledge
from ontology.daa_graph_builder import build_daa_graph
from urllib.parse import unquote
from rag.dedup_utils import dedupe_chunks
# from processors.video_processor import transcribe_video

app = FastAPI(title="AI Education System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_engine = RAGEngine()
memory_engine = MemoryEngine()
hierarchy_engine = HierarchyEngine()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "AI Education Backend is running"
    }

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):

    uploaded_files = []

    for file in files:

        filename = file.filename

        if not filename:
            continue

        extension = Path(filename).suffix.lower()

        if extension not in [".pdf", ".pptx"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {filename}"
            )

        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # --------------------------------
        # Extract text
        # --------------------------------

        if extension == ".pdf":
            text = extract_pdf_text(file_path)
        else:
            text = extract_ppt_text(file_path)

        # --------------------------------
        # Generate topic-aware chunks
        # --------------------------------

        hierarchy, topic_chunks = hierarchy_engine.generate_hierarchy(
            text,
            filename,
            []
        )

        # --------------------------------
        # Store topic-aware chunks in FAISS
        # --------------------------------

        rag_engine.add_document(topic_chunks)

        # --------------------------------
        # ONTOLOGY KNOWLEDGE EXTRACTION
        # --------------------------------

        extracted_knowledge = extract_relationships(text)

        validated_knowledge = validate_knowledge(
            extracted_knowledge
        )

        build_daa_graph(
            validated_knowledge
        )

        # --------------------------------
        # Response
        # --------------------------------

        uploaded_files.append({
            "filename": filename,
            "characters": len(text),
            "chunks": topic_chunks,
            "hierarchy": hierarchy
        })

    return {
        "files_uploaded": len(uploaded_files),
        "documents": uploaded_files
    }

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):

    # Check video type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid video file."
        )

    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    # Save video
    video_path = UPLOAD_DIR / filename

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # --------------------------------
    # Run Whisper in a separate process
    # --------------------------------

    try:

        result = subprocess.run(
            [
                sys.executable,
                "processors/transcribe_worker.py",
                str(video_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        transcript = result.stdout.strip()

    except subprocess.CalledProcessError as e:

        print("Whisper worker error:")
        print(e.stderr)

        raise HTTPException(
            status_code=500,
            detail="Video transcription failed."
        )

    # --------------------------------
    # Generate hierarchy
    # --------------------------------

    hierarchy, topic_chunks = hierarchy_engine.generate_hierarchy(
        transcript,
        filename,
        []
    )

    # --------------------------------
    # Add to RAG
    # --------------------------------

    rag_engine.add_document(topic_chunks)

    return {
        "filename": filename,
        "characters": len(transcript),
        "transcript": transcript,
        "chunks": topic_chunks,
        "hierarchy": hierarchy
    }


@app.get("/hierarchy")
def get_hierarchy():
    return hierarchy_engine.store.get_hierarchy()

@app.get("/knowledge-graph")
def get_knowledge_graph():
    return convert_graph_to_json()

@app.get("/knowledge-graph/node/{node_name}")
def get_node_context(node_name: str):

    node_name = unquote(node_name)

    matching_chunks = []

    for chunk in rag_engine.vector_store.chunks:

        content = chunk.get("content", "")
        topic = chunk.get("topic", "")
        subtopic = chunk.get("subtopic", "")

        # Prefer exact topic/subtopic matches
        if (
            node_name.lower() == topic.lower()
            or node_name.lower() == subtopic.lower()
        ):
            matching_chunks.append(chunk)

    # If no exact topic/subtopic match,
    # search for the node name inside chunk content
    if not matching_chunks:

        for chunk in rag_engine.vector_store.chunks:

            content = chunk.get("content", "")

            if node_name.lower() in content.lower():
                matching_chunks.append(chunk)

    # Remove near-duplicate chunks (same info, reworded by the LLM on a
    # re-upload/reprocess) using word-overlap similarity rather than
    # exact-text similarity, then cap how much material is returned.
    matching_chunks = dedupe_chunks(matching_chunks, threshold=0.6)[:5]

    return {
        "node": node_name,
        "chunks": matching_chunks
    }


class Question(BaseModel):
    question: str
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    document: Optional[str] = None
    
def is_memory_question(question: str):
    memory_phrases = [
        "what did we just discuss",
        "what did we just talk about",
        "what were we just discussing",
        "what did we discuss",
        "what did we talk about",
        "remind me what we discussed",
        "remind me what we talked about",
        "what was my last question",
        "what did i just ask",
        "what did i ask just now",
    ]

    question_lower = question.lower()

    return any(
        phrase in question_lower
        for phrase in memory_phrases
    )


@app.post("/ask")
def ask_question(request: Question):

    memory_only = is_memory_question(request.question)

    # 1. Retrieve relevant study material
    if memory_only:
        relevant_chunks = []

    elif request.topic and request.subtopic:
        # Subtopic-specific AI
        relevant_chunks = rag_engine.retrieve(
            request.question,
            top_k=3,
            topic=request.topic,
            subtopic=request.subtopic
        )

    else:
        # Global AI — search across all study material
        relevant_chunks = rag_engine.retrieve(
            request.question,
            top_k=5
        )

    # 2. Create RAG context
    if memory_only:
        context = """
        The student is asking about their conversation history.

        Do not use the study material to answer this question.
        """

    elif request.topic and request.subtopic:
        context = f"""
        Current Study Context:
        Document: {request.document}
        Topic: {request.topic}
        Subtopic: {request.subtopic}

        Relevant Study Material:
        """

    else:
        context = """
        The student is asking a general question about their uploaded study material.

        Relevant Study Material:
        """

    for chunk in relevant_chunks:
        context += f"""
        Topic: {chunk['topic']}
        Subtopic: {chunk['subtopic']}
        Content: {chunk['content']}
        """

    # 3. Retrieve student's previous interactions
    memories = memory_engine.get_relevant_memories(
        request.question,
        top_k=5
    )

    memory_context = ""

    if memories:
        memory_context = """
        CONVERSATION HISTORY

        The interactions below are listed from OLDEST to NEWEST.
        Use their order when answering questions about what happened
        before, after, earlier, later, or most recently.

        """

        for i, memory in enumerate(memories, start=1):
                    memory_context += f"""
        Interaction {i}:
        User: {memory['question']}
        AI: {memory['answer']}

        """

    else:
        memory_context = """
        No previous conversation history is available.
        """

    # 4. Build the contextual question for Gemini
    if memory_only:

        contextual_question = f"""
        The student is asking about their conversation history.

        Use the CONVERSATION HISTORY provided to answer the question.

        Important instructions:
        - Treat the conversation history as chronological.
        - The interactions are ordered from OLDEST to NEWEST.
        - "Most recent" means the LAST interaction.
        - "Before" means an earlier interaction.
        - "After" means a later interaction.
        - Do not use the uploaded study material to answer this question.
        - Do not invent conversations that are not present in the history.

        Student's question:
        {request.question}
        """

    elif request.topic and request.subtopic:

        contextual_question = f"""
        The student is currently studying:

        Document: {request.document}
        Topic: {request.topic}
        Subtopic: {request.subtopic}

        Answer the student's question using the provided study material.

        Student's question:
        {request.question}
        """

    else:

        contextual_question = f"""
        The student is asking a general question about their uploaded study material.

        Answer the student's question using the provided study material.

        Student's question:
        {request.question}
        """

    # 5. Send study material + conversation memory to Gemini
    answer = ask_ai(
        contextual_question,
        context + "\n\n" + memory_context
    )

    # 6. Save the new interaction
    memory_engine.remember(
        request.question,
        answer,
        request.document,
        request.topic,
        request.subtopic
    )

    return {
        "question": request.question,
        "retrieved_chunks": relevant_chunks,
        "answer": answer,
        "memory_used": memories
    }