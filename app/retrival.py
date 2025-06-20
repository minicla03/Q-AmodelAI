import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA


def ask_question(qa_chain, query, language_hint="italiano"):
    prompt = f"Rispondi in {language_hint}. " + query
    result = qa_chain.invoke(prompt)
    return result["result"], result["source_documents"]

def compute_exact_match(prediction, ground_truth):
    return int(prediction.strip().lower() == ground_truth.strip().lower())

def compute_f1(prediction, ground_truth):
    pred_tokens = prediction.lower().split()
    gt_tokens = ground_truth.lower().split()
    common = set(pred_tokens) & set(gt_tokens)
    if len(common) == 0:
        return 0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1
