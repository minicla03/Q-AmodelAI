from abc import ABC

from langchain_classic.chains.llm import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from rag_logic.llm.LLM import LLM
from rag_logic.tools.QATool import QATool
from persistence.model.Flashcard import Flashcard
import json

from rag_logic.utils import json_to_toon, toon_to_json


class FlashcardTool(QATool, ABC):
    def __init__(self):
        super().__init__()

    def execute(self, retriever, query, language_hint="italian", toon_format: bool = False, n_flashcard=10, difficulty = "medium"):

        user_query_str = query.get("user_query", "")

        filtered_docs = self._retrieve_documents(retriever, query)

        if not filtered_docs:
            return {"type": "FLASHCARD",
                    "result": [],
                    "ai_response": "Nessun dato"}

        system_prompt = f"""
            You are an AI assistant that generates study flashcards from a given text. 
            The flashcards should help a student learn key concepts efficiently.
    
            Requirements:
            - Generate {n_flashcard} flashcards.
            - Each flashcard must have:
              - a clear question
              - a concise answer
            - Difficulty level: {difficulty}
            - Language: {language_hint}
            - Respond ONLY in valid JSON format as a list of objects:
              [
                {{"question": "...", "answer": "..."}},
                ...
              ]
              
            Make sure questions are precise, answers are correct, and avoid extra commentary.
        """

        user_prompt = """
            Context:
            {filtered_docs}
            
            User question:
            {query}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        flash_chain = (
            prompt
            | LLM()
            | StrOutputParser()
        )

        try:
            json_result = flash_chain.invoke({
                "context":  self.format_docs(filtered_docs),
                "question": user_query_str,
                 "language": language_hint
            })

            json_str = json_result.replace("```json", "").replace("```", "").strip()

            flashcards_data = json.loads(json_str)

            flashcard_objects = [Flashcard(answer=ft["answer"], question=ft["question"]) for ft in flashcards_data]

            return {
                "type": "FLASHCARD",
                "result": flashcard_objects,
                "docs_source": filtered_docs,
                "metadata": {
                    "language": language_hint,
                    "n_flashcards": n_flashcard,
                    "difficulty": difficulty
                }
            }

        except Exception as e:

            print(f"Errore generazione Flashcards: {e}")
            return {
                "type": "FLASHCARD",
                "result": [],
                "ai_response": f"Errore durante la generazione: {str(e)}"
            }

