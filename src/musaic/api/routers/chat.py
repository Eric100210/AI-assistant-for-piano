"""Route de conversation avec l'assistant théorique (RAG)."""

from fastapi import APIRouter

from musaic.api.schemas import ChatRequest, ChatResponse
from musaic.api.services import answer_question, build_history_messages

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Répond à une question sur la progression (RAG sur les cours de théorie).

    L'API est sans état : le front renvoie l'historique de la conversation
    dans ``payload.history`` à chaque requête.
    """
    history = build_history_messages(payload.history)
    response = answer_question(payload.query, history)
    return ChatResponse(response=response)
