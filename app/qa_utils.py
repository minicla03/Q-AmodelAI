'''
Utility functions for question-answering tasks using LangChain.
This module provides functions to clean text, ask questions, and handle responses.
'''

def clean_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = ' '.join(text.split())
    return text

def ask_question(qa_chain, query, language_hint="italiano"):
    prompt = f"Rispondi in {language_hint}. {query}"
    result = qa_chain.invoke(prompt)
    return result["result"], result["source_documents"]
