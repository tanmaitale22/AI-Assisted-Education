# Memory Importance Scoring Prototype

This project implements a secure persistent memory scoring prototype for AI agents using Python 3.11, FastAPI, SQLite, SQLAlchemy, Sentence Transformers, and scikit-learn.

## Features

- Rule-based candidate extraction with optional LLM classifier interface
- Feature scoring for preference, long-term relevance, frequency, task relevance, confidence, and recency
- Weighted adaptive scoring from JSON config
- Explainable decision engine
- SQLite persistence for stored memories
- FastAPI endpoints for scoring and memory listing/deletion
- Evaluation script with dataset and metrics

## Project Layout

- `memory_scoring/app/api`
- `memory_scoring/app/models`
- `memory_scoring/app/services`
- `memory_scoring/app/scoring`
- `memory_scoring/app/extractors`
- `memory_scoring/app/database`
- `memory_scoring/app/config`
- `memory_scoring/app/evaluation`
- `memory_scoring/app/tests`

## Installation

```bash
cd memory_scoring
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run API

```bash
uvicorn main:app --reload
```

## Example Requests

### Score a conversation

```bash
curl -X POST http://127.0.0.1:8000/score \
  -H "Content-Type: application/json" \
  -d '{"conversation":"My favorite language is Python. I work as a software engineer.", "agent_profile":"Coding Assistant"}'
```

### List memories

```bash
curl http://127.0.0.1:8000/memory
```

### Delete memory

```bash
curl -X DELETE http://127.0.0.1:8000/memory/1
```

## Extensions

The architecture allows later plug-ins for trust validation, prompt injection detection, memory provenance, versioning, encryption, RBAC, and explainable retrieval through the interface abstractions.
