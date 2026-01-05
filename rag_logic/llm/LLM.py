from __future__ import annotations

import json
import logging

from langchain_core.prompt_values import StringPromptValue, ChatPromptValue

logger = logging.getLogger(__name__)

import threading
from typing import Any, List, Dict

from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output
from ollama import Client
from dotenv import load_dotenv
import os

from rag_logic.utils import toon_to_json, json_to_toon


class LLM(Runnable):

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
            model: str = "gpt-oss:120b-cloud",
            temperature: float = 0.1,
            top_p: float = 0.95,
            top_k: int = 40
    ):
        if getattr(self, "_initialized", False):
            return

        self.model = model
        self.default_options = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_ctx": 4096,
            "repeat_penalty": 1.1
        }

        self.__initialize_client()
        self._initialized = True
        logger.info(f"LLM Singleton initialized with model: {self.model}")

    def __initialize_client(self):
        load_dotenv(override=True)

        api_key = os.getenv("RAG_C")
        host = os.getenv("OLLAMA_HOST", "https://ollama.com")

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self.__client = Client(
            host=host,
            headers=headers if headers else None
        )

    def invoke(self, input: Input, config: RunnableConfig | None = None, **kwargs: Any) -> Output:

        messages = self._convert_input_to_messages(input)

        toon_format = kwargs.get("toon_format", False)
        if toon_format:
            messages = json_to_toon(messages)

        logger.debug(f"Invoking LLM with model {self.model}. Input messages: {len(messages)}")

        current_options = self.default_options.copy()
        for key in current_options.keys():
            if key in kwargs:
                current_options[key] = kwargs[key]

        model_to_use = kwargs.get("model", self.model)

        try:
            response = self.__client.chat(
                model=model_to_use,
                messages=messages,
                options=current_options,
                stream=False
            )

            logger.info(f"LLM Response received (Model: {model_to_use})")


            if isinstance(response, dict):
                content = response.get("message", {}).get("content", "")
            elif hasattr(response, "message"):
                content = response.message.content
            else:
                try:
                    parsed = json.loads(response)
                    content = parsed.get("message", {}).get("content", "")
                except (json.JSONDecodeError, TypeError):
                    content = str(response)

            if kwargs.get("toon_format", False):
                content = toon_to_json(content)

            return content

        except Exception as e:
            logger.error(f"Error during LLM invocation: {e}", exc_info=True)
            raise e

    def _convert_input_to_messages(self, input: Input) -> List[Dict[str, str]]:
        """Helper method to normalize input into a list of messages."""
        if isinstance(input, str):
            return [{"role": "user", "content": input}]

        elif isinstance(input, StringPromptValue):
            return [{"role": "user", "content": input.text}]

        elif isinstance(input, ChatPromptValue):
            messages = []
            for m in input.messages:
                if m.type == 'human':
                    role = 'user'
                elif m.type == 'ai':
                    role = 'assistant'
                elif m.type == 'system':
                    role = 'system'
                elif m.type == 'chat':
                    role = getattr(m, 'role', 'user')
                else:
                    role = 'user'

                messages.append({"role": role, "content": m.content})
            return messages

        elif isinstance(input, dict):
            if "messages" in input:
                return input["messages"]
            elif "text" in input:
                return [{"role": "user", "content": input["text"]}]
            else:
                content = input.get("input") or str(input)
                return [{"role": "user", "content": content}]

        else:
            return [{"role": "user", "content": str(input)}]