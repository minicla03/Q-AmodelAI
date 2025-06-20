'''
Utility functions for question-answering tasks using LangChain.
This module provides functions to clean text, ask questions, and handle responses.
'''

import re

LANGUAGE_ALIASES = {
    "italian": ["italiano", "italian"],
    "english": ["inglese", "english"],
    "french": ["francese", "french"],
    "spanish": ["spagnolo", "spanish"],
    "german": ["tedesco", "german"]
}

def clean_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = ' '.join(text.split())
    return text


def detect_language_from_query(query):
    query_lower = query.lower()
    for lang, aliases in LANGUAGE_ALIASES.items():
        for alias in aliases:
            if re.search(r"\b(in|in lingua|in lingua)\s+" + re.escape(alias) + r"\b", query_lower) or f"rispondi in {alias}" in query_lower:
                return lang
    return None