'''
Questo modulo gestisce l'ingestione dei dati da documenti PDF che
verranno utilizzati per creare una base di conoscenza per l'applicazione.
Include funzioni per estrarre testo dai file PDF, processare il testo,
creare embedding e memorizzare i dati in un vector store.
'''

import shutil
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from qa_utils import clean_text

def setup_qa_system(pdf_path="data", persist_dir="chroma_db", force_rebuild=False):
    # Controlla se ricostruire il vector store
    if force_rebuild or not os.path.exists(persist_dir):
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print(f"[DEBUG] Rebuilding vector store...")

        print(f"[DEBUG] Creazione del vector store da PDF in {pdf_path}")  
        documents = []
        for filename in os.listdir(pdf_path):
            if filename.endswith(".pdf"):
                filepath = os.path.join(pdf_path, filename)
                loader = PyPDFLoader(filepath)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = filename  # Imposta solo il nome del file come fonte
                    if clean_text(doc.page_content):
                        documents.append(doc)
        
        # chunck dei documenti Invece di tagliare semplicemente 
        # il testo a una lunghezza fissa, utilizza una 
        # gerarchia di separatori predefiniti per trovare i punti di 
        # divisione più naturali. 
        # I separatori di default sono ["\n\n", "\n", " ", ""], il che significa che proverà prima a dividere sui 
        # paragrafi (doppio newline), poi sulle righe singole, poi sugli spazi, 
        # e infine sui caratteri individuali come ultima risorsa.
        splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=200)
        chunks = splitter.split_documents(documents)
        print(chunks[5:7])
        
        # creazione degli embedding
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        print("[DEBUG] HuggingFaceEmbeddings object created")

        sample_texts = [chunk.page_content for chunk in chunks[:1]]
        sample_embeddings = embeddings.embed_documents(sample_texts)
        print("[DEBUG] Sample embeddings:", sample_embeddings)

        vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
        print(f"[DEBUG] Vector store created with {len(chunks)} chunks")
        
    else:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        print("[DEBUG] Loaded existing vector store")
    
    llm = ChatOllama(model="llama3:latest", temperature=0.1, top_p=0.95, top_k=40)
    retriever = vectorstore.as_retriever(search_type="similarity", k=3)
    
    # factory method che crea automaticamente una catena preconfigurata, semplificando  
    # la configurazione rispetto alla creazione manuale di tutti i componenti.
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    return qa_chain

def add_document_to_vectorstore(file_path, persist_dir="chroma_db"):
    """
    Aggiunge un nuovo documento PDF al vectorstore Chroma esistente.
    """
    print(f"[DEBUG] Caricamento documento: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    vectorstore.add_documents(chunks)
    print(f"[DEBUG] Vector store created with {len(chunks)} chunks")
    print(f"[DEBUG] Persistenza completata")

def delete_document_from_vectorstore(file_name, persist_dir="chroma_db"):
    """
    Elimina i chunk associati a un file specifico dal vectorstore Chroma.

    Args:
        file_name (str): Il nome del file PDF da eliminare.
        persist_dir (str): La directory dove si trova il vectorstore.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

     # Metodo più efficiente usando where clause
    file_name = os.path.splitext(file_name)[0]  # Rimuove l'estensione
        
    # Prima verifica quanti documenti ci sono con questo source
    results = vectorstore.get(where={"source": file_name})
    
    if not results['ids']:
        print(f"[WARNING] Nessun chunk trovato per il file '{file_name}'")
    
    try:
        ids_to_delete = []
        docs_in_store = vectorstore.get()
        
        target = os.path.splitext(file_name.lower())[0]
        for doc_id, doc_meta in zip(docs_in_store['ids'], docs_in_store['metadatas']):
            source = os.path.splitext(doc_meta.get("source", "").lower())[0]
            if source == target:
                ids_to_delete.append(doc_id)

        print(f"[DEBUG] Trovati {len(ids_to_delete)} chunk da eliminare per il file '{file_name}'")

        if ids_to_delete:
            vectorstore.delete(ids=ids_to_delete)
            print(f"[DEBUG] Eliminati {len(ids_to_delete)} chunk relativi a '{file_name}' dal vectorstore.")

    except Exception as e:
        print(f"[ERROR] Errore durante l'eliminazione dei chunk dal vectorstore: {e}")
