def ask_question(qa_chain, query, language_hint="italian", max_sources=3, similarity_threshold=0.75):
    '''
    Risponde a una domanda utilizzando un sistema di QA basato su un chain di recupero e generazione.
    Args:
        qa_chain (RetrievalQA): Il chain di QA da utilizzare per rispondere alla domanda.
        query (str): La domanda a cui rispondere.
        language_hint (str): Suggerimento di lingua per la risposta.
    '''
    # Esegue una ricerca nel vectorstore per ottenere i documenti pertinenti ricercando per similarità
    vectorstore = qa_chain.retriever.vectorstore
    retrieved_docs_with_scores = vectorstore.similarity_search_with_score(query, k=10)

    # Filtra i documenti recuperati in base alla soglia di similarità
    filtered_docs_with_scores = [(doc, score) for doc, score in retrieved_docs_with_scores if score >= similarity_threshold]
    # Limita il numero di documenti a quelli richiesti
    filtered_docs_with_scores = filtered_docs_with_scores[:max_sources]
    # Estrae solo i documenti filtrati
    filtered_docs = [doc for doc, _ in filtered_docs_with_scores]

    if not filtered_docs:
        return "Informazione non presente nel contesto.", []

    # Prepara il prompt per la generazione della risposta
    prompt = (
        f"Rispondi in {language_hint} in modo chiaro e semplice, "
        "spiegando i concetti principali in modo comprensibile anche a chi non è esperto. "
        "La risposta deve includere i dettagli fondamentali, come definizioni, caratteristiche essenziali, "
        "ma senza usare un linguaggio troppo tecnico o complicato. "
        "Sii sintetico ma completo, come se stessi spiegando a uno studente o collega che vuole capire bene l'argomento.\n\n"
        f"Domanda: {query}"
        "Basati esclusivamente sulle informazioni fornite nel contesto per costruire una risposta accurata e completa."
    )

    # Combina i documenti recuperati e il prompt per generare la risposta
    result = qa_chain.combine_documents_chain.invoke(input={
        "input_documents": filtered_docs,
        "question": prompt
    })

    return result, filtered_docs
