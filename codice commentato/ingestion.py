"""
Modulo per l'Ingestione di Documenti PDF per la Knowledge Base

Questo modulo si occupa dell'intera pipeline per creare e mantenere una knowledge base
a partire da documenti PDF. Le funzionalità principali includono:

1. Estrazione e pulizia del testo dai PDF
2. Suddivisione in chunk e elaborazione del testo
3. Generazione di embedding con modelli multilingue
4. Creazione e mantenimento dello vector store
5. Configurazione del sistema QA con capacità di retrieval

Tecnologie utilizzate:
- PyPDFLoader per l'estrazione del testo da PDF
- Embedding di HuggingFace per la vettorizzazione
- ChromaDB per lo storage vettoriale
- Modello LLM Ollama per il question answering
"""

import shutil
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from qa_utils import clean_text

"""
Inizializza e configura l'intero sistema QA con document retrieval.

Parametri:
    pdf_path (str): Percorso alla directory contenente i documenti PDF
    persist_dir (str): Directory per salvare/caricare il database vettoriale
    force_rebuild (bool): Forza la ricostruzione dello vector store

Restituisce:
    RetrievalQA: Catena QA configurata e pronta per rispondere a domande

Funzionamento:
1. Verifica se lo vector store deve essere ricostruito
2. Elabora tutti i PDF nella directory
3. Crea chunk di testo con overlap
4. Genera embedding e li memorizza
5. Configura il sistema QA aumentato con retrieval
"""

def setup_qa_system(pdf_path="data", persist_dir="chroma_db", force_rebuild=False):

    # 1. Logica per la ricostruzione del vector store
    if force_rebuild or not os.path.exists(persist_dir):
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print(f"[DEBUG] Ricostruzione del vector store in corso...")
        
        # 2. Elabora tutti i PDF nella directory
        documents = []
        for filename in os.listdir(pdf_path):
            if filename.endswith(".pdf"):
                filepath = os.path.join(pdf_path, filename)
                loader = PyPDFLoader(filepath)
                docs = loader.load()
                for doc in docs:
                    # Memorizza solo il nome del file come metadato
                    doc.metadata["source"] = filename
                    # Aggiunge solo documenti non vuoti dopo la pulizia
                    if clean_text(doc.page_content).strip():
                        documents.append(doc)
        
        # 3. Suddivide i documenti in chunk con overlap
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,  # Dimensione ottimale per bilanciare contesto e precisione
            chunk_overlap=200  # Garantisce continuitÃ  del contesto tra i chunk
        )
        chunks = splitter.split_documents(documents)
        
        # 4. Crea gli embedding e lo vector store
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        vectorstore = Chroma.from_documents(
            chunks, 
            embeddings, 
            persist_directory=persist_dir
        )
        vectorstore.persist()
        print(f"[DEBUG] Vector store creato con {len(chunks)} chunk")
        
    else:  # Carica uno vector store esistente
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        vectorstore = Chroma(
            persist_directory=persist_dir, 
            embedding_function=embeddings
        )
        print("[DEBUG] Caricamento dello vector store esistente")
    
    # 5. Configura il modello LLM con parametri ottimizzati
    llm = ChatOllama(
        model="llama3:latest",
        temperature=0.1,  # Valore basso per risposte piÃ¹ deterministiche
        max_tokens=512,   # Limita la lunghezza delle risposte
        top_p=0.95,       # Parametro per il nucleus sampling
        top_k=40          # Parametro per il top-k sampling
    )
    
    # 6. Configura il retriever dei documenti
    retriever = vectorstore.as_retriever(
        search_type="similarity",  # Usa la ricerca per similaritÃ 
        k=3  # Restituisce i 3 documenti piÃ¹ rilevanti
    )
    
    # 7. Crea la catena QA finale
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True  # Restituisce le fonti per verifica
    )
    
    return qa_chain

"""
Aggiunge un documento PDF a uno vector store esistente.

Parametri:
    file_path (str): Percorso al file PDF da aggiungere
    persist_dir (str): Directory dello vector store esistente

Processo:
    1. Carica e suddivide il documento PDF
    2. Genera embedding per i nuovi chunk
    3. Li aggiunge allo vector store esistente
    4. Rende persistenti le modifiche
"""

def add_document_to_vectorstore(file_path, persist_dir="chroma_db"):
    print(f"[DEBUG] Caricamento documento: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # 1. Suddivide il documento usando gli stessi parametri iniziali
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)
    
    # 2. Carica lo stesso modello di embedding usato originariamente
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # 3. Si connette al vector store esistente
    vectorstore = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=persist_dir
    )
    
    # 4. Aggiunge i nuovi chunk e rende persistenti le modifiche
    vectorstore.add_documents(chunks)
    print(f"[DEBUG] Aggiunti {len(chunks)} nuovi chunk allo vector store")
    print(f"[DEBUG] Persistenza completata")