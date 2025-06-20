def ask_question(qa_chain, query, language_hint="italiano"):
    #system prompt and query
    prompt = f"Rispondi in {language_hint}. " + query
    result = qa_chain.invoke(prompt)
    return result["result"], result["source_documents"]


