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
J’ai joué une progression I - VIm - IV : 
On me conseille de jouer maintenant un accord parmi les suivants : V - I. 
Explique l’effet créé par ces progressions possibles et propose des variantes pertinentes avec le style de musique qui leur est souvent associé.
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
                "Bienvenue dans l'assistant musical MusAIc ! Posez vos questions sur les progressions musicales que vous jouez."
            )
        while True:
            if not initial_query:
                user_input = input("Votre question: ")
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("À bientôt !")
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
