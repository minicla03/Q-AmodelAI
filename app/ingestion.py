'''
This module handles the ingestion of data from pdf documents that
will be used to create a knowledge base for the application.
It includes functions to extract text from PDF files, process the text,
create embeddings, and store the data in a vector store.
'''

import shutil
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from qa_utils import clean_text


def setup_qa_system(pdf_path="data", persist_dir="chroma_db", force_rebuild=False):
    # Controlla se ricostruire il vector store
    if force_rebuild or not os.path.exists(persist_dir):
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print(f"[DEBUG] Rebuilding vector store...")
        
        documents = []
        for filename in os.listdir(pdf_path):
            if filename.endswith(".pdf"):
                filepath = os.path.join(pdf_path, filename)
                loader = PyPDFLoader(filepath)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = filename  # Imposta solo il nome del file come fonte
                    if clean_text(doc.page_content).strip():
                        documents.append(doc)
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=200)
        chunks = splitter.split_documents(documents)
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
        vectorstore.persist()
        print(f"[DEBUG] Vector store created with {len(chunks)} chunks")
        
    else:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        print("[DEBUG] Loaded existing vector store")
    
    llm = ChatOllama(model="llama3:latest", temperature=0.1, max_tokens=512, top_p=0.95, top_k=40)
    retriever = vectorstore.as_retriever(search_type="mmr", k=5)
    
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    return qa_chain

def add_document_to_vectorstore(pdf_path, persist_dir="chroma_db"):
    if not os.path.exists(pdf_path) or not pdf_path.endswith(".pdf"):
        raise ValueError(f"[ERROR] File non valido: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Aggiungi nome file ai metadati per tracciamento fonte
    filename = os.path.basename(pdf_path)
    for doc in documents:
        doc.metadata["source"] = filename

    documents = [doc for doc in documents if clean_text(doc.page_content).strip()]
    if not documents:
        print(f"[DEBUG] Nessun contenuto utile in {pdf_path}")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    vectorstore.add_documents(chunks)
    vectorstore.persist()
    print(f"[DEBUG] Aggiunto {len(chunks)} chunk da: {filename}")