def ask_question(qa_chain, query, language_hint="italian"):
    prompt = (
        f"Rispondi in {language_hint} in modo chiaro e specifico, "
        "fornendo uno o due dettagli importanti senza essere troppo tecnico o prolisso. "
        "Mantieni la risposta concisa e facilmente comprensibile anche da chi non è esperto.\n"
        f"Domanda: {query}"
    )
    result = qa_chain.invoke(prompt)
    return result["result"], result["source_documents"]
