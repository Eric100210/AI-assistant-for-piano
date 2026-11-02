"""Chat route for the theory assistant (RAG)."""

from fastapi import APIRouter

from musaic.api.schemas import ChatRequest, ChatResponse
from musaic.api.services import answer_question, build_history_messages

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Answer a question about the progression (RAG over the theory courses).

    The API is stateless: the frontend sends the conversation history in
    ``payload.history`` with every request.
    """
    history = build_history_messages(payload.history)
    response = answer_question(payload.query, history)
    return ChatResponse(response=response)
