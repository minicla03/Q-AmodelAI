from dataclasses import dataclass
from typing import Optional


@dataclass
class Flashcard:
    notebook_id: str
    user_id: str
    question: str
    answer: str
    _id: Optional[str] = None

    def to_dict(self):
        return {
            'notebook_id': self.notebook_id,
            'user_id': self.user_id,
            'question': self.question,
            'answer': self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Flashcard":
        return cls(
            notebook_id=data.get("notebook_id") or data.get("id_notebook"), # Fallback per sicurezza
            user_id=data.get("user_id") or data.get("id_user"),
            question=data.get("question"),
            answer=data.get("answer"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )