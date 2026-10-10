from retrieval_pipeline import retrieve_documents, generate_response
from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

LLM_MODEL = "llama3.2:3b"

TEST_QUERY = """
J’ai joué une progression I - VIm - IV : 
On me conseille de jouer maintenant un accord parmi les suivants : V - I. 
Explique l’effet créé par ces progressions possibles et propose des variantes pertinentes avec le style de musique qui leur est souvent associé.
"""


llm = OllamaLLM(model=LLM_MODEL, base_url="http://localhost:11434")


class LLMChat:
    def __init__(self):
        self.chat_history = []

    def ask_question(self, query):
        if self.chat_history:
            # Ask AI to make the question standalone
            messages = (
                SystemMessage(
                    content="Etant donné l'historique du chat, reformule la nouvelle question pour qu'elle soit autonome et compréhensible sans contexte :"
                ),
                *self.chat_history,
                HumanMessage(content=f"Nouvelle question : {query}"),
            )
            result = llm.invoke(messages)
            standalone_query = result.strip()
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
