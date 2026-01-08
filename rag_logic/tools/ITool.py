from __future__ import annotations

import importlib
from abc import abstractmethod, ABC


class Context:

    def __init__(self, strategy: IToolStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> IToolStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: IToolStrategy) -> None:
        self._strategy = strategy

    def execute(self, *args, **kwargs) -> dict:
        return self._strategy.execute(*args, **kwargs)


class ContextFactory:
    @staticmethod
    def create(tool_name: str) -> Context | None:
        try:
            tool_name = tool_name.lower()
            tool_map = {
                "qa_tool": ("rag_logic.tools.QATool", "QATool"),
                "flashcard_tool": ("rag_logic.tools.FlashcardTool", "FlashcardTool"),
                "quiz_tool": ("rag_logic.tools.QuizTool", "QuizTool"),
            }

            if tool_name not in tool_map:
                raise ValueError(f"Tool '{tool_name}' non riconosciuto")

            module_name, class_name = tool_map[tool_name]
            module = importlib.import_module(module_name)
            tool_class = getattr(module, class_name)
            return Context(tool_class())
        except KeyError:
            return None


class IToolStrategy(ABC):

    def _retrieve_documents(self, retriever, user_query):
        if hasattr(retriever, "retrieve_and_explain"):
            print("Retrieving documents and explaining...")
            return retriever.retrieve_and_explain(user_query)
        return retriever.invoke(user_query)

    def format_docs(self, docs):
        if isinstance(docs[0], dict):
            return "\n\n".join(item.get("document_content", "") for item in docs)
        return "\n\n".join(doc.page_content for doc in docs)

    @abstractmethod
    def execute(self, retriever, query: dict, language: str = "italian") -> dict:
        pass
