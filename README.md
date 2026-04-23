# Codebase QA Copilot

A minimal document QA service built with FastAPI, Chroma, local embeddings, and Claude.

## Features

- ingest local Markdown and TXT files
- split content with paragraph-aware chunking and long-paragraph fallback windows
- store embeddings in Chroma with richer chunk metadata
- retrieve relevant chunks with score filtering, dedupe, merge, and context budgeting
- answer with source citations and richer source metadata
- stay grounded in indexed documents and return `根据当前文档无法确定。` when retrieval evidence is weak

## Project layout

```text
app/
  core/
  routers/
  services/
  config.py
  main.py
  schemas.py
data/docs/
docs/
tests/
```

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
copy .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

### Run with Docker

Build the image:

```bash
docker build -t codebase-qa-copilot .
```

Run the container:

```bash
docker run --rm -p 8000:8000 --env-file .env codebase-qa-copilot
```

If you want Chroma data to persist outside the container, mount the data directory:

```bash
docker run --rm -p 8000:8000 --env-file .env -v "$(pwd)/data:/app/data" codebase-qa-copilot
```

Open:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

## Environment variables

See `.env.example`.

Important values:
- `DEFAULT_DOCS_DIR`: default source directory for local docs
- `CHROMA_PERSIST_DIRECTORY`: local Chroma persistence path
- `EMBEDDING_MODEL_NAME`: sentence-transformers model
- `CHUNK_SIZE`: target chunk size
- `CHUNK_OVERLAP`: overlap used for long-segment fallback chunking
- `DEFAULT_TOP_K`: default number of final sources returned by `/qa`
- `RETRIEVAL_FETCH_K`: number of initial vector hits fetched before filtering
- `RETRIEVAL_SCORE_THRESHOLD`: minimum retrieval score retained as usable evidence
- `GROUNDED_TOP_SCORE_THRESHOLD`: minimum top score required for grounded answers
- `GROUNDED_AVERAGE_SCORE_THRESHOLD`: minimum average score required for grounded answers
- `GROUNDED_MIN_CHUNKS`: minimum number of valid chunks required after filtering
- `MAX_CONTEXT_CHARS`: approximate context budget passed to the prompt
- `ENABLE_RERANK`: reserved switch for future rerank stage
- `RERANK_TOP_N`: reserved rerank scope
- `ANTHROPIC_API_KEY`: required for Claude-generated answers
- `ANTHROPIC_MODEL`: defaults to `claude-opus-4-6`

If `ANTHROPIC_API_KEY` is empty, the app still runs and returns a grounded extractive fallback answer.

When running in Docker, the default paths still point to `data/docs` and `data/chroma` inside the container. Mounting `./data:/app/data` keeps the same layout while persisting indexed content on the host.

## Sample flow

### 1. Ingest docs

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"docs_dir": "data/docs"}'
```

### 2. Ask a question

```bash
curl -X POST http://127.0.0.1:8000/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the assistant support?", "top_k": 3}'
```

### Error responses

HTTP errors now use a consistent JSON shape:

```json
{
  "detail": "No indexed content found. Please ingest documents first.",
  "request_id": "7e7f0b17-2c41-4a25-9137-4dc289b6f2f0"
}
```

The service also returns an `X-Request-ID` response header so request logs can be correlated with API failures.

## Endpoints

### `GET /health`
Basic service health.

### `POST /ingest`
Loads `.md` and `.txt` files, splits them with paragraph-aware chunking, embeds them, and indexes them into Chroma with chunk offsets and section metadata.

Request:

```json
{
  "docs_dir": "data/docs"
}
```

### `POST /qa`
Retrieves candidate chunks, applies score filtering and retrieval post-processing, builds a grounded prompt, and returns an answer, a grounding flag, and scored sources.

Request:

```json
{
  "question": "What does the product support?",
  "top_k": 3
}
```

Response when evidence is sufficient:

```json
{
  "answer": "The system supports POST /qa for question answering.",
  "grounded": true,
  "sources": [
    {
      "source": "data/docs/product.md",
      "file_type": "md",
      "chunk_index": 0,
      "snippet": "POST /qa answers questions.",
      "score": 0.91,
      "distance": 0.09,
      "start_offset": 0,
      "end_offset": 42,
      "title": null,
      "section": "API"
    }
  ]
}
```

Response when evidence is insufficient:

```json
{
  "answer": "根据当前文档无法确定。",
  "grounded": false,
  "sources": [
    {
      "source": "data/docs/overview.txt",
      "file_type": "txt",
      "chunk_index": 0,
      "snippet": "This project uses FastAPI and Chroma.",
      "score": 0.41,
      "distance": 0.59,
      "start_offset": 0,
      "end_offset": 36,
      "title": null,
      "section": "overview"
    }
  ]
}
```

## Tests

```bash
pytest
```

Targeted verification used for the retrieval v2 upgrade:

```bash
python -m pytest "D:/python/Codebase QA Copilot/tests/test_splitter.py" "D:/python/Codebase QA Copilot/tests/test_retrieval_service.py" "D:/python/Codebase QA Copilot/tests/test_qa.py" "D:/python/Codebase QA Copilot/tests/test_ingest.py"
```

## Notes

- This version keeps the original `/ingest -> VectorStore -> RetrievalService -> /qa` flow.
- Retrieval v2 improves quality mainly through metadata, score-based filtering, paragraph-aware chunking, dedupe/merge, and context budgeting.
- `score` is currently derived from Chroma distance using a simple `1 - distance` mapping for filtering and display.
- Only `.md` and `.txt` files are indexed.
- No authentication or UI is included.
- Chroma persists data locally under `data/chroma`.
