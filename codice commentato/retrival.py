"""
Gestisce il processo completo di ricerca e generazione di risposte a una domanda.

Parametri:
    qa_chain (RetrievalQA): Catena QA configurata
    query (str): Domanda dell'utente
    language_hint (str): Lingua preferita per la risposta (default: "italian")
    max_sources (int): Numero massimo di fonti da considerare (default: 3)
    similarity_threshold (float): Soglia di similarità per filtrare i documenti (default: 0.75)

Returns:
    tuple: (risposta_generata, lista_documenti_usati)

Processo:
    1. Recupera documenti rilevanti dallo vector store
    2. Filtra per similarità e numero massimo di fonti
    3. Costruisce un prompt ottimizzato per la chiarezza
    4. Genera la risposta finale usando la catena QA
"""

def ask_question(qa_chain, query, language_hint="italian", max_sources=3, similarity_threshold=0.75):
    # 1. Recupero documenti con punteggi di similarità
    vectorstore = qa_chain.retriever.vectorstore
    retrieved_docs_with_scores = vectorstore.similarity_search_with_score(query, k=10)

    # 2. Filtraggio documenti per soglia di similarità
    filtered_docs_with_scores = [
        (doc, score) 
        for doc, score in retrieved_docs_with_scores 
        if score >= similarity_threshold
    ]
    
    # Limita al numero massimo di fonti richiesto
    filtered_docs_with_scores = filtered_docs_with_scores[:max_sources]
    
    # Estrae solo i documenti (senza punteggi)
    filtered_docs = [doc for doc, _ in filtered_docs_with_scores]

    # Gestione caso nessun documento trovato
    if not filtered_docs:
        return "Informazione non presente nel contesto.", []

    # 3. Costruzione prompt ottimizzato
    prompt = (
        f"Rispondi in {language_hint} in modo chiaro e semplice, "
        "spiegando i concetti principali in modo comprensibile anche a chi non è esperto. "
        "La risposta deve includere i dettagli fondamentali, come definizioni, caratteristiche essenziali, "
        "ma senza usare un linguaggio troppo tecnico o complicato. "
        "Sii sintetico ma completo, come se stessi spiegando a uno studente o collega che vuole capire bene l'argomento.\n\n"
        f"Domanda: {query}"
        "Basati esclusivamente sulle informazioni fornite nel contesto per costruire una risposta accurata e completa."
    )

    # 4. Generazione risposta finale
    result = qa_chain.combine_documents_chain.invoke(input={
        "input_documents": filtered_docs,
        "question": prompt
    })

    return result, filtered_docs