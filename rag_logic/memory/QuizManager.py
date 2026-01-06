from typing import List

from persistence.IxRepository import IRepos
from persistence.model.Quiz import Quiz
from rag_logic.memory.ChatManager import logger


class QuizManager:
    def __init__(self, repository: IRepos.IQuizRepository, notebook_id: str, user_id: str):
        self.repository = repository
        self.notebook_id = notebook_id
        self.user_id = user_id
        self._buffer: List[Quiz] = []

    def add_to_buffer(self, quiz_data):
        clean_objects = []
        for item in quiz_data:
            if isinstance(item, Quiz):
                item.notebook_id = self.notebook_id
                item.user_id = self.user_id
                clean_objects.append(item)
            elif isinstance(item, dict):
                clean_objects.append(
                    Quiz(
                        notebook_id=self.notebook_id,
                        user_id=self.user_id,
                        question=item.get("question"),
                        answer_list=item.get("answer_list"),
                        correct_answer=item.get("correct_answer"),
                        difficulty=item.get("difficulty", "medium")
                    )
                )

        self._buffer.extend(clean_objects)

    def persist_buffer(self):
        if not self._buffer:
            return 0

        count = 0
        try:
            for q in self._buffer:
                data = q.to_dict()
                self.repository.create_quiz(data)
                count += 1
            self._buffer.clear()
            return count
        except Exception as e:
            logger.error(f"Errore salvataggio quiz: {e}", exc_info=True)
            return 0

    def get_all(self) -> list:
        try:
            db_quizzes = self.repository.get_quiz_by_notebook(str(self.notebook_id))
        except Exception:
            db_quizzes = []

        ram_quizzes = []
        for idx, quiz in enumerate(self._buffer):
            data = quiz.to_dict()
            data['_id'] = f"ram_{idx}"
            data['is_unsaved'] = True
            ram_quizzes.append(data)

        return db_quizzes + ram_quizzes

    def delete(self, quiz_id: str) -> bool:
        if quiz_id.startswith("ram_"):
            try:
                idx = int(quiz_id.split("_")[1])
                if 0 <= idx < len(self._buffer):
                    self._buffer.pop(idx)
                    return True
            except (ValueError, IndexError):
                return False
            return False

        return self.repository.delete_quiz(quiz_id)