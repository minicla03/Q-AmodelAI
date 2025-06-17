import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA

def clean_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = ' '.join(text.split())
    return text

def setup_qa_system(pdf_path="data/Android.pdf", persist_dir="chroma_db"):
    # Carica e pulisci PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    for doc in documents:
        doc.page_content = clean_text(doc.page_content)
    
    # Split in chunk
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    # Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Vectorstore Chroma
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    vectorstore.persist()
    
    # LLM Ollama
    llm = ChatOllama(model="gemma:2b")
    
    retriever = vectorstore.as_retriever(search_type="similarity", k=10)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

def ask_question(qa_chain, query, language_hint="italiano"):
    # Per evitare risposte in inglese, puoi aggiungere un suggerimento
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
