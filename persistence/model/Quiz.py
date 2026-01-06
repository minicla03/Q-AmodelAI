from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Quiz:
    notebook_id: str
    user_id: str
    question: str
    answer_list: List[str]
    difficulty: str
    correct_answer: str
    _id: Optional[str] = None

    def to_dict(self):
        return {
            'notebook_id': self.notebook_id,
            'user_id': self.user_id,
            'question': self.question,
            'answer_list': self.answer_list,
            'difficulty': self.difficulty,
            'correct_answer': self.correct_answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        return cls(
            notebook_id=data.get("notebook_id") or data.get("id_notebook"),
            user_id=data.get("user_id"),
            question=data.get("question"),
            answer_list=data.get("answer_list"),
            difficulty=data.get("difficulty"),
            correct_answer=data.get("correct_answer"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )


