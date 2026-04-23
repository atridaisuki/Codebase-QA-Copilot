import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.schemas import AgentRequest, AgentResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentResponse)
def agent_chat(request: AgentRequest) -> AgentResponse:
    service = AgentService()
    return service.chat(
        message=request.message,
        conversation_id=request.conversation_id,
    )


@router.post("/chat/stream")
def agent_chat_stream(request: AgentRequest) -> EventSourceResponse:
    service = AgentService()

    def event_generator():  # type: ignore[no-untyped-def]
        for event in service.chat_stream(
            message=request.message,
            conversation_id=request.conversation_id,
        ):
            yield {"event": event["event"], "data": event["data"]}

    return EventSourceResponse(event_generator())
