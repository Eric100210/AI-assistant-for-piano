"""Conversational RAG: chat history and standalone-question reformulation.

The interactive loop is kept here for convenience; ``musaic.cli`` drives it.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from musaic.rag.llm import get_llm
from musaic.rag.retrieval import (
    generate_response,
    retrieve_documents,
    make_standalone_query,
)

TEST_QUERY = """
I played a I - VIm - IV progression:
I'm advised to play one of the following chords next: V - I.
Explain the effect of these possible progressions and suggest relevant variations, along with the music styles they are often associated with.
"""


class LLMChat:
    def __init__(self):
        self.chat_history = []

    def ask_question(self, query):
        if self.chat_history:
            # Ask AI to make the question standalone
            standalone_query = make_standalone_query(query, self.chat_history)
        else:
            standalone_query = query
        return standalone_query

    def start_chat(self, initial_query=None):
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

            query = self.ask_question(
                user_input
            )  # reformulate the question to be standalone

            # Generate response using the retrieval pipeline
            documents = retrieve_documents(query)
            response = generate_response(query, documents)

            # Remember the conversation in chat_history
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=response))
            initial_query = None

            print(f"MusAIc: {response}")


if __name__ == "__main__":
    chat = LLMChat()
    print(chat.chat_history)
    chat.start_chat(initial_query=TEST_QUERY)
