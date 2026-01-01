import json
from abc import ABC

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from persistence.model.Quiz import Quiz
from rag_logic.llm.LLM import LLM
from rag_logic.tools.QATool import QATool


class QuizTool(QATool, ABC):

    def __init__(self):
        super().__init__()

    def execute(self, retriever, query, language_hint: str = "italian", toon_format: bool = False, n_questions=5,
                difficulty="medium"):

        filtered_docs = self._retrieve_documents(retriever, query)

        if not filtered_docs:
            return {"type": "QUIZ", "result": [], "ai_response": "Nessun dato"}


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
        - Respond ONLY in valid JSON format as a list of objects.
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

        chain = (
                {
                    "context": retriever | self.format_docs(filtered_docs),
                    "question": RunnablePassthrough(),
                    "language": RunnablePassthrough(),
                }
                | prompt
                | LLM()
        )

        try:
            json_result = chain.invoke({"question": query, "language": language_hint})
            json_str = json_result["output_text"]

            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            quiz_data = json.loads(json_str)
        except Exception as e:
            print(f"Errore parsing JSON: {e}")
            raise ValueError("Output non in formato JSON valido")

        quiz = [
            Quiz(
                id_notebook=qt["id_notebook"],
                question=qt["question"],
                answer_list=qt["answer_list"],
                correct_answer=qt["correct_answer"],
                difficulty=qt.get("difficulty", difficulty)
            )
            for qt in quiz_data
        ]

        return {
            "type": "QUIZ",
            "result": quiz,
            "docs_source": filtered_docs,
            "metadata": {"language": language_hint, "n_questions": n_questions, "difficulty": difficulty}
        }