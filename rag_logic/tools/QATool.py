from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from rag_logic.llm.LLM import LLM
from rag_logic.tools.ITool import IToolStrategy


class QATool(IToolStrategy):

    def __init__(self):
        super().__init__()

    def execute(self, retriever, query: dict, language="italian", toon_format: bool = False):

        user_query = query["user_query"]
        summary = query["summary"]

        filtered_docs = self._retrieve_documents(retriever, user_query)

        if not filtered_docs:
            return {
                "type": "QA",
                "ai_response": "Informazione non presente nel contesto.",
                "docs_source": [],
                "metadata": {"language": language}
            }

        # Prepara il prompt per la generazione della risposta
        system_prompt = f"""
            Answer in {language} clearly and simply,
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
                """

        if summary:
            user_prompt += """
                Storia Chat (Opzionale):
                {summary}
            """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        qa_chain = (
                {
                    "context": retriever | self.format_docs(filtered_docs),
                    "question": RunnablePassthrough(),
                    "summary": RunnablePassthrough(),
                    "language": RunnablePassthrough()
                }
                | prompt
                | LLM()
                | StrOutputParser()
        )

        response = qa_chain.invoke({
            "question": user_query,
            "summary": summary,
            "language": language
        })

        return  {
            "type": "QA",
            "ai_response": response["output_text"] ,
            "docs_source": filtered_docs,
            "metadata": {"language": language}
        }
