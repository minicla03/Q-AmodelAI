from typing import List


class AgentState:
    def __init__(self, query: str, language_hint: str = "italian", message_count: int = 0):
        self.query = query
        self.language_hint = language_hint
        self.message_count = message_count
        self.docs: List[str] = []
        self.history: List[str] = []
        self.steps: int = 0
        self.done: bool = False
        self.answer: str = ""
        self.summary: str = ""
        self.retriever = None