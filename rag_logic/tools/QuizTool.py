import json
from abc import ABC

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from rag_logic.llm.LLM import LLM
from rag_logic.tools.ITool import IToolStrategy


class QuizTool(IToolStrategy):

    def __init__(self):
        super().__init__()

    def execute(self, retriever, query, language_hint: str = "italian", toon_format: bool = False, n_questions=5,
                difficulty="medium"):

        user_query_str = query.get("user_query", "")

        filtered_docs = self._retrieve_documents(retriever, user_query_str)

        if not filtered_docs:
            return {"type": "QUIZ", "result": [],
                    "ai_response": "Nessun dato"}

        system_prompt = f"""
        You are an AI assistant that generates multiple-choice quiz questions from a given text.

        Requirements:
        - Generate {n_questions} quiz questions.
        - Each quiz must have:
            - "question": a clear question
            - "answer_list": a list of 3-4 possible answers
            - "correct_answer": the correct answer (must be one of the options in answer_list)
            - "difficulty": "{difficulty}"
        - Language: {language_hint}
        - Respond ONLY in valid JSON format as a list of objects:
          [
            {{{{ 
                "question": "...", 
                "answer_list": ["A", "B", "C"], 
                "correct_answer": "A",
                "difficulty": "{difficulty}"
            }}}},
            ...
          ]
        - answer_list must include 3-4 options: one correct answer and 2-3 plausible distractors.
        - Avoid obviously wrong answers.
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

        quiz_chain = (
                prompt
                | LLM()
                | StrOutputParser()
        )

        try:
            json_result = quiz_chain.invoke({
                "filtered_docs": self.format_docs(filtered_docs),
                "query": user_query_str,
                "language": language_hint
            })

            json_str = json_result.replace("```json", "").replace("```", "").strip()
            quiz_data = json.loads(json_str)

            return {
                "type": "QUIZ",
                "result": quiz_data,
                "docs_source": filtered_docs,
                "metadata": {
                    "language": language_hint,
                    "n_questions": n_questions,
                    "difficulty": difficulty
                },
                "ai_response": f"Ho generato {len(quiz_data)} quiz. Digita /quiz per vederli o salvarli."
            }
        except Exception as e:
            print(f"Errore generazione Quiz: {e}")
            return {
                "type": "QUIZ",
                "result": [],
                "ai_response": f"Errore durante la generazione dei quiz: {str(e)}"
            }