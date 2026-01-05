from persistence.IxRepository import IRepos
from rag_logic.memory.ChatManager import logger


class QuizManager:
    def __init__(self, repository: IRepos.IQuizRepository, notebook_id: str, user_id: str):
        self.repository = repository
        self.notebook_id = notebook_id
        self.user_id = user_id
        self._buffer = []

    def add_to_buffer(self, quiz):
        if quiz:
            self._buffer.append(quiz)

    def persist_buffer(self):
        if not self._buffer:
            return 0

        count = 0
        try:
            for q in self._buffer:
                data = q.to_dict() if hasattr(q, 'to_dict') else q
                data['notebook_id'] = self.notebook_id
                data['user_id'] = self.user_id
                self.repository.create_quiz(data)
                count += 1
            self._buffer.clear()
            return count
        except Exception as e:
            logger.error(f"Errore salvataggio quiz: {e}")
            return 0

    def get_all(self) -> list:
        try:
            db_quizzes = self.repository.get_quiz_by_notebook(str(self.notebook_id))
        except Exception:
            db_quizzes = []

        ram_quizzes = []
        for idx, quiz in enumerate(self._buffer):
            data = quiz.to_dict() if hasattr(quiz, 'to_dict') else quiz.copy()
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