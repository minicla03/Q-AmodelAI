'''
Funzioni di utilità per la gestione delle domande e risposte.
Queste funzioni includono:
- detect_language_from_query: per rilevare la lingua della domanda basata su parole chiave.
- clean_text: per pulire il testo rimuovendo spazi e caratteri non necessari.
- LANGUAGE_ALIASES: un dizionario per mappare le lingue a nomi alternativi.
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
    #text = text.replace('\n', ' ').replace('\t', ' ')
    #text = ' '.join(text.split())
    text = re.sub(r'\s+', ' ', text)
    return text.split

def detect_language_from_query(query):
    query_lower = query.lower()
    for lang, aliases in LANGUAGE_ALIASES.items():
        for alias in aliases:
            if re.search(r"\b(in|in lingua)\s+" + re.escape(alias) + r"\b", query_lower) or f"rispondi in {alias}" in query_lower:
                return lang
    return None