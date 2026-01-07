import os
import shutil

from persistence.IxRepository import IRepos
from rag_logic.ingestion.ingestion import IngestionFlow
from rag_logic.memory.ChatManager import logger


class DocumentManager:
    def __init__(self, notebook_repo: IRepos.INotebookRepository, notebook_id: str, chat_id: str, doc_path: str):
        self.notebook_repo = notebook_repo
        self.notebook_id = notebook_id
        self.chat_id = chat_id
        self.doc_path = doc_path

        self.ingestion = IngestionFlow(self.notebook_id)

    @property
    def retriever(self):
        """Espone il retriever per la RAG pipeline."""
        return self.ingestion.retriever

    def reload_ingestion(self):
        """Ricarica il vectorstore (utile al restart)."""
        self.ingestion.reload_vectorstore()

    def add_document(self, file_path: str):
        if not os.path.exists(file_path):
            logger.error(f"File non trovato: {file_path}")
            return False

        try:
            os.makedirs(self.doc_path, exist_ok=True)
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(self.doc_path, file_name)

            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                shutil.copy(file_path, dest_path)

            self.ingestion.add_document_to_vectorstore(dest_path)
            self.notebook_repo.update_chat_metadata(self.notebook_id, self.chat_id, docs=[dest_path])
            logger.info(f"Documento '{file_name}' aggiunto.")
            return True

        except Exception as e:
            logger.error(f"Errore add_document: {e}", exc_info=True)
            return False

    def delete_document(self, file_name: str) -> bool:
        file_path = os.path.join(self.doc_path, file_name)
        try:
            self.ingestion.delete_document_from_vectorstore(file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File '{file_name}' rimosso.")
            # self.notebook_repo.remove_doc_from_metadata(...) # TODO
            return True
        except Exception as e:
            logger.error(f"Errore delete_document: {e}")
            return False

    def list_documents(self) -> list:
        try:
            return self.notebook_repo.get_list_docs(self.notebook_id) or []
        except Exception as e:
            logger.error(f"Errore list_documents: {e}")
            return []