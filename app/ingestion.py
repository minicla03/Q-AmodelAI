'''
This module handles the ingestion of data from pdf documents that
will be used to create a knowledge base for the application.
It includes functions to extract text from PDF files, process the text,
create embeddings, and store the data in a vector store.
'''

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from qa_utils import clean_text

def setup_qa_system(pdf_path="data/Android.pdf", persist_dir="chroma_db"):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Clean the text content of each document
    documents = [
        doc for doc in documents
        if clean_text(doc.page_content).strip()
    ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    vectorstore.persist()

    llm = ChatOllama(model="llama3:latest", temperature=0.1, max_tokens=512, top_p=0.95, top_k=40)
    retriever = vectorstore.as_retriever(search_type="similarity", k=10)

    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    return qa_chain