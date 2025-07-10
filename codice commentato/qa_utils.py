"""
Modulo di utilità per attività di question-answering con LangChain

Questo modulo fornisce funzioni per:
- Pulire e normalizzare il testo
- Rilevare la lingua dalle query
- Gestire le risposte del sistema QA
"""

import re

# Dizionario di alias linguistici per il rilevamento automatico della lingua
# Formato: {lingua_principale: [lista_alias]}
LANGUAGE_ALIASES = {
    "italian": ["italiano", "italian"],
    "english": ["inglese", "english"],
    "french": ["francese", "french"],
    "spanish": ["spagnolo", "spanish"],
    "german": ["tedesco", "german"]
}

def clean_text(text):
    """
    Pulisce e normalizza il testo rimuovendo caratteri speciali e spazi superflui
    """
    # Sostituisce newline e tab con spazi
    text = text.replace('\n', ' ').replace('\t', ' ')
    # Rimuove spazi multipli e riduce a singoli spazi
    text = ' '.join(text.split())
    return text

def detect_language_from_query(query):
    """
    Rileva automaticamente la lingua richiesta in una query
    Logica di rilevamento:
    1. Cerca pattern come "in italiano" o "rispondi in inglese"
    2. Confronta con gli alias linguistici definiti
    3. Restituisce la lingua principale se trovata
    """
    query_lower = query.lower()
    
    # Scansiona tutte le lingue e i loro alias
    for lang, aliases in LANGUAGE_ALIASES.items():
        for alias in aliases:
            # Cerca corrispondenze con espressioni regolari
            pattern = r"\b(in|in lingua|in lingua)\s+" + re.escape(alias) + r"\b"
            if re.search(pattern, query_lower) or f"rispondi in {alias}" in query_lower:
                return lang
                
    # Nessuna lingua rilevata
    return None