import glob
import logging
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA

from rag_logic.ingestion.DocumentLoaderStrategy import *
from rag_logic.llm.LLM import LLM

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

class IngestionFlow(object):
    """
    The IngestionFlow class manages the full ingestion process of external documents
    into a vector-based knowledge store. It performs the following tasks:
     - Load text from various file formats via loader strategies
     - Split documents into manageable chunks
     - Generate embeddings for semantic search
     - Store and persist chunks in a Chroma vector database
     - Provide a retrieval-enabled QA chain integrated with an LLM
    """

    def __init__(self, notebook_id: str):
        """
        Initializes the ingestion flow with embedding, vector store, retriever,
        and large language model (LLM) configurations.
        """

        self.persist_dir = f"chroma_db/{notebook_id}"

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

        self.vectorstore = Chroma(
                    collection_name="chat_docs",
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_dir)

        self.retriever_vs = self.vectorstore.as_retriever(search_type="similarity", k=3)
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=200)
        self.llm = LLM() #ChatOllama(model="llama3:latest", temperature=0.1, top_p=0.95, top_k=40)
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=self.retriever_vs, return_source_documents=True)
        #self.qa_chain = create_retrieval_chain(self.retriever_vs, self.llm)

        self.strategies = {
            ".pdf": PDFLoaderStrategy(),
            ".docx": WordLoaderStrategy(),
            ".txt": TextLoaderStrategy(),
            ".html": WebLoaderStrategy(),
            ".url": WebLoaderStrategy(),
            ".csv": CSVLoaderStrategy(),
        }

        logger.info(f"IngestionFlow initialized for notebook '{notebook_id}'.")

    def reload_vectorstore(self):
        """

        """
        if not os.path.exists(self.persist_dir):
            raise FileNotFoundError(f"Nessun database Chroma trovato in '{self.persist_dir}'.")

        logger.info(f"Riapertura vectorstore da '{self.persist_dir}'...")

        self.vectorstore = Chroma(
            collection_name="chat_docs",
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )

        self.retriever_vs = self.vectorstore.as_retriever(search_type="similarity", k=3)
        self.qa_chain.retriever = self.retriever_vs
        logger.info("Vectorstore ricaricato con successo.")
        return True

    def add_document_to_vectorstore(self, file_path: str):
        """
        Adds a new document to the vector store by:
          1. Loading it using the appropriate strategy.
          2. Splitting into smaller text chunks.
          3. Embedding and storing them in Chroma.

        Args:
            file_path (str): Path to the input file.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")

        ext = os.path.splitext(file_path)[1].lower()
        strategy = self.strategies.get(ext)

        if not strategy:
            raise ValueError(f"No strategy defined for file format '{ext}'")

        logger.info(f"Loading document: {file_path}")

        documents = strategy.load(file_path)

        for doc in documents:
            if "source" not in doc.metadata:
                doc.metadata["source"] = file_path

        chunks = self.splitter.split_documents(documents)

        if not chunks:
            logger.warning(f"No chunks generated from document '{file_path}'.")
            return

        self.vectorstore.add_documents(chunks)

        logger.info(f"Added {len(chunks)} chunks from '{file_path}' to vectorstore.")

    def add_documents_from_folder(self, folder_path: str):
        """
        Aggiunge tutti i documenti presenti in una cartella al vectorstore.
        Solo i file con estensioni supportate (.pdf, .docx, .txt, .html, .url, .csv)
        verranno processati.

        Args:
            folder_path (str): Percorso della cartella contenente i documenti.
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Cartella '{folder_path}' non trovata.")

        files_added = 0
        for ext in self.strategies.keys():
            pattern = os.path.join(folder_path, f"*{ext}")
            for file_path in glob.glob(pattern):
                try:
                    self.add_document_to_vectorstore(file_path)
                    files_added += 1
                except Exception as e:
                    logger.exception(f"Errore aggiungendo '{file_path}': {e}")

        if files_added == 0:
            logger.warning(f"Nessun file valido trovato in '{folder_path}'.")
        else:
            logger.info(f"Aggiunti {files_added} file da '{folder_path}' al vectorstore.")

    def delete_document_from_vectorstore(self, file_name: str):
        """
        Deletes all chunks associated with a specific file from the Chroma vector store.

        Args:
            file_name (str): The name of the source file to remove.
        """

        file_name = os.path.splitext(file_name)[0]

        try:
            results = self.vectorstore.get(include=["metadatas"])
            ids_to_delete = []

            target_name = os.path.basename(file_name)

            for i, meta in enumerate(results["metadatas"]):
                source_path = meta.get("source", "")
                if os.path.basename(source_path) == target_name:
                    ids_to_delete.append(results["ids"][i])

            if ids_to_delete:
                self.vectorstore.delete(ids=ids_to_delete)
                logger.info(f"Eliminati {len(ids_to_delete)} chunk per il file '{target_name}'")
            else:
                logger.warning(f"Nessun chunk trovato per '{target_name}'")

        except Exception as e:
            logger.exception(f"Errore cancellazione: {e}")
