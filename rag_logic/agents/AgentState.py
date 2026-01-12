from typing import List, Optional


class AgentState:
    def __init__(self, user_query: str, message_count: int = 0):
        self._has_answer: bool = False
        self.user_query = user_query
        self.language_hint = None
        self.message_count = message_count

        self.docs = []
        self.answer = ""
        self.summary = ""
        self.explanation: list = []

        self.history: List[str] = []
        self.steps = 0
        self.done = False

        self.retriever = None
        self.has_summary = False
        self.summary_reason: Optional[str] = None  # "implicit" | "explicit"

    @property
    def has_answer(self) -> bool:
        return self._has_answer

    @has_answer.setter
    def has_answer(self, value):
        self._has_answer = value
