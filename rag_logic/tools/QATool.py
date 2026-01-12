from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from rag_logic.llm.LLM import LLM
from rag_logic.tools.ITool import IToolStrategy


class QATool(IToolStrategy):

    def __init__(self):
        super().__init__()

    def execute(self, retriever, query: dict):
        user_query = query.get("user_query")
        summary = query.get("summary", "Nessuna storia precedente disponibile.")

        filtered_docs = self._retrieve_documents(retriever, user_query)
        language = self._detect_language_from_query(user_query)

        if language:
            lang_instruction = f"Answer in {language}"
            target_metadata = language
        else:
            lang_instruction = "Answer in the same language used in the User Query"
            target_metadata = "auto-detected"

        if not user_query:
            return {
                "type": "ERROR",
                "ai_response": "Si è verificato un errore interno: query mancante.",
                "docs_source": [],
                "metadata": {"language": target_metadata}
            }

        if not filtered_docs:
            print("[QATool] Nessun documento trovato nel contesto. Interruzione anticipata.")
            return {
                "type": "QA",
                "ai_response": "Informazione non presente nel contesto.",
                "docs_source": [],
                "metadata": {"language": target_metadata}
            }

        system_prompt = f"""
            {lang_instruction} clearly and simply,
            explaining the main concepts in a way that’s easy to understand even for non-experts.
            The answer should include the essential details, such as definitions and key characteristics,
            but without using overly technical or complex language.
            Be concise yet complete, as if you were explaining the topic to a student or colleague who wants to fully understand it.\n\n
            Rely exclusively on the information provided in the context to construct an accurate and complete answer.
        """

        user_prompt = """
            Contesto:
            {context}

            Domanda Utente: 
            {user_query}

            Storia Chat (Opzionale):
            {summary}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        qa_chain = (
                prompt
                | LLM()
                | StrOutputParser()
        )

        response = qa_chain.invoke({
            "context": self.format_docs(filtered_docs),
            "user_query": user_query,
            "summary": summary,
        })

        if filtered_docs and isinstance(filtered_docs[0], dict):
            final_sources = filtered_docs
        else:
            final_sources = [
                {
                    "document_content": doc.page_content,
                    "metadata": doc.metadata,
                    "explanation_text": "Recuperato tramite similarità standard.",
                    "score": 0.0
                }
                for doc in filtered_docs
            ]

        return {
            "type": "QA",
            "ai_response": response,
            "docs_source": final_sources,
            "metadata": {"language": target_metadata}
        }