import json
from abc import ABC

from persistence.model.Quiz import Quiz
from rag_logic.tools.QATool import QATool


class QuizTool(QATool, ABC):

    def __init__(self):
        super().__init__()

    def execute(self, qa_chain, query, language_hint: str = "italian", toon_format: bool = False, n_questions=5,
                difficulty="medium"):

        filtered_docs = self._retrieve_documents(qa_chain, query)

        if not filtered_docs:
            return {"type": "QUIZ", "result": [], "ai_response": "Nessun dato"}

        context_text = "\n\n".join([d.page_content for d in filtered_docs])

        prompt = f"""
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

        Text to process:
        {context_text}
        """

        input_to_chain = {"input_documents": filtered_docs, "question": prompt}

        response = qa_chain.combine_documents_chain.invoke(
            input=input_to_chain,
            config=None,
            toon_format=toon_format
        )

        try:
            json_str = response["output_text"]

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