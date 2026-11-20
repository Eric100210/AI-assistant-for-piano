"""Conversational RAG: chat history and standalone-question reformulation.

The interactive loop is kept here for convenience; ``musaic.cli`` drives it.
"""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from musaic.rag.retrieval import answer_question


class LLMChat:
    def __init__(self) -> None:
        self.chat_history: list[BaseMessage] = []

    def start_chat(self, initial_query: str | None = None) -> None:
        if not initial_query:
            print(
                "Welcome to the MusAIc music assistant! Ask questions about the chord progressions you play."
            )
        while True:
            if not initial_query:
                user_input = input("Your question: ")
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break
            else:
                user_input = initial_query

            response = answer_question(user_input, self.chat_history)

            # Remember the conversation in chat_history
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=response))
            initial_query = None

            print(f"MusAIc: {response}")
