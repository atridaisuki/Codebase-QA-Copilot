from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.schemas import IngestRequest, IngestResponse
from app.services.bm25_service import BM25Service
from app.services.document_loader import DocumentLoader
from app.services.embedding_service import EmbeddingService
from app.services.text_splitter import TextSplitter
from app.services.vector_store import VectorStore

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(request: IngestRequest) -> IngestResponse:
    settings = get_settings()
    docs_dir = request.docs_dir or settings.default_docs_dir

    loader = DocumentLoader()
    splitter = TextSplitter()
    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    try:
        documents = loader.load_directory(docs_dir)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not documents:
        raise HTTPException(status_code=400, detail="No supported documents found to ingest.")

    chunks = splitter.split_documents(documents)
    embeddings = embedding_service.embed_documents([chunk.content for chunk in chunks])
    vector_store.upsert_chunks(chunks, embeddings)

    bm25_service = BM25Service()
    bm25_service.index(chunks)

    return IngestResponse(
        files_count=len(documents),
        chunks_count=len(chunks),
        collection_name=vector_store.collection_name,
    )
