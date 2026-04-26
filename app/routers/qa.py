from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.core.prompt_builder import build_qa_prompt
from app.schemas import QARequest, QAResponse
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.services.vector_store import VectorStore

router = APIRouter(tags=["qa"])


@router.post("/qa", response_model=QAResponse)
def ask_question(request: QARequest) -> QAResponse:
    settings = get_settings()
    retrieval_service = RetrievalService()
    llm_service = LLMService()
    vector_store = VectorStore()

    top_k = request.top_k or settings.default_top_k
    context, sources = retrieval_service.retrieve(request.question, top_k=top_k)

    if vector_store.count() == 0:
        raise HTTPException(status_code=400, detail="No indexed content found. Please ingest documents first.")

    if not retrieval_service.has_sufficient_evidence(request.question, sources):
        return QAResponse(answer="根据当前文档无法确定。", grounded=False, sources=sources)

    #context发给llm
    prompt = build_qa_prompt(question=request.question, context=context)
    answer = llm_service.generate_answer(prompt=prompt, sources=sources)

    #传sources提供答案来源，实现答案可溯源
    return QAResponse(answer=answer, grounded=True, sources=sources)

