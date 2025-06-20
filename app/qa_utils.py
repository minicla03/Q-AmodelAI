'''
Utility functions for question-answering tasks using LangChain.
This module provides functions to clean text, ask questions, and handle responses.
'''

def clean_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = ' '.join(text.split())
    return text
