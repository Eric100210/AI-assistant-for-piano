"""Chat route for the theory assistant (RAG)."""

from fastapi import APIRouter

from musaic.api.schemas import ChatRequest, ChatResponse
from musaic.api.services import build_history_messages
from musaic.rag.retrieval import answer_question

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Answer a question about the progression (RAG over the theory courses).

    The API is stateless: the frontend sends the conversation history in
    ``payload.history`` with every request.
    """
    history = build_history_messages(payload.history)
    context = (
        payload.analysis.model_dump_json(exclude={"fileName"})
        if payload.analysis is not None
        else None
    )
    response = answer_question(payload.query, history, context=context)
    return ChatResponse(response=response)
