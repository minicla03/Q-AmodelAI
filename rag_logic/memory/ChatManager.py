import logging
import os
import shutil
import traceback

from persistence.long_term_memory.mongo.MongoDBMS import MongoConnectionManager
from persistence.long_term_memory.mongo.NotebookRepository import MongoNotebookRepository
from rag_logic.ingestion.ingestion import IngestionFlow
from rag_logic.utils import  detect_language_from_query

from rag_logic.agents.routing_agent import router_agent
from rag_logic.agents.summarizer_agent import summary_agent

from rag_logic.tools.ITool import ContextFactory

from persistence.IxRepository import IRepos
from persistence.short_term_memory.redis.RedisDBMS import RedisConnectionManager
from persistence.short_term_memory.redis.ChatRepository import ChatRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

class ChatManager:
    """
       Manages a chat session for a user, including document management,
       chat history, and execution of the RAG (Retrieval-Augmented Generation) pipeline.
    """

    MIN_MESSAGES_FOR_SUMMARY = 5

    def __init__(
            self,
            user_id: str,
            notebook_id: str,
            chat_id: str,
            notebook_repo: IRepos.INotebookRepository,
            chat_repo: IRepos.IChatRepository,
            ingestion_flow,
            document_path: str = "docs"
    ):

        self.user_id = user_id
        self.notebook_id = notebook_id
        self.chat_id = chat_id
        self.document_path = document_path

        # Iniezione delle dipendenze
        self.notebook_repository = notebook_repo
        self.chat_repository = chat_repo
        self.ingestion_layer = ingestion_flow

        self.last_summary = ""
        self.ready = True

        try:
            self.last_summary = self.notebook_repository.get_last_summary(self.chat_id) or ""
            logger.info(
                f"ChatManager inizializzato per user {self.user_id} (Summary preesistente: {bool(self.last_summary)})")
        except Exception as e:
            logger.error(f"Errore recupero summary iniziale: {e}")

    def _restart(self):
        """
        Restores an existing chat session from the repository.
        """
        self.ingestion_layer = IngestionFlow(self.notebook_id)
        self.ingestion_layer.reload_vectorstore()
        self.ready = True

    def execute_rag_pipeline(self, user_query, default_language="italian", memory_ability=True, toon_format=False):

        logger.info("Avvio pipeline RAG per query utente: %s", user_query)

        try:
            self.chat_repository.add_message(self.chat_id, {"type": "human", "mex": user_query})
            logger.info("User message added to chat history.")
        except Exception as e:
            logger.warning("Failed to save user message: %s", e)

        logger.info("Messaggio utente aggiunto alla cronologia.")

        language = detect_language_from_query(user_query) or default_language
        logger.info("Lingua rilevata: %s", language)

        if not self.ingestion_layer or not self.ingestion_layer.qa_chain:
            logger.warning("Pipeline RAG non pronta")
            return {"error": "Sistema QA non pronto", "ai_response": None}

        tool_name = router_agent(user_query, toon_format, language)
        logger.info(f"Tool selezionato dal router: {tool_name}")

        context = ContextFactory.create(tool_name)
        if not context:
            logger.error(f"ContextFactory ha restituito None per il tool '{tool_name}'")
            return {"error": f"Tool '{tool_name}' non supportato o errore di creazione", "ai_response": None}

        if memory_ability:
            try:
                history_mex = self.chat_repository.get_messages(self.chat_id)
                if len(history_mex) >= self.MIN_MESSAGES_FOR_SUMMARY:
                    logger.info("Aggiornamento summary conversazione...")
                    self.last_summary = summary_agent(history_mex, toon_format, language_hint=language)
                    logger.info("Summary aggiornato.")
            except Exception as e:
                logger.warning(f"Errore durante l'aggiornamento del summary: {e}")

        query={
            "user_query": user_query,
            "summary": self.last_summary,
        }

        try:
            logger.info("Esecuzione catena RAG con il contesto selezionato...")
            response = context.execute(self.ingestion_layer.qa_chain, query, language, toon_format=toon_format)
            ai_response = response.get("ai_response", "")

            self.chat_repository.add_message(self.chat_id, {"type": "system", "mex": ai_response})
            logger.info("AI response saved to chat history.")
            logger.info("Esecuzione completata con successo.")
            return response
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error("Errore durante l'esecuzione della pipeline RAG: %s", str(e))
            logger.debug("Traceback completo:\n%s", tb_str)
            return {
                "error": f"Errore interno: {str(e)}",
                "traceback": tb_str,
                "ai_response": None
            }

    def add_document(self, file_path: str):
        if not os.path.exists(file_path):
            logger.error(f"File non trovato: {file_path}")
            return

        try:
            os.makedirs(self.document_path, exist_ok=True)

            file_name = os.path.basename(file_path)
            dest_path = os.path.join(self.document_path, file_name)

            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                shutil.copy(file_path, dest_path)
                logger.info(f"Documento copiato in: {dest_path}")

            self.ingestion_layer.add_document_to_vectorstore(dest_path)

            self.notebook_repository.update_chat_metadata(self.notebook_id, self.chat_id, docs=[dest_path])
            logger.info(f"Documento '{file_name}' aggiunto e indicizzato con successo.")

        except Exception as e:
            logger.error(f"Errore durante l'aggiunta del documento '{file_path}': {e}", exc_info=True)

    def delete_document(self, file_name: str) -> bool:
    
        file_path = os.path.join(self.document_path, file_name)

        logger.info(f"Richiesta eliminazione documento: {file_name}")

        try:
            self.ingestion_layer.delete_document_from_vectorstore(file_name)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File fisico '{file_path}' rimosso.")
            else:
                logger.warning(f"File fisico '{file_path}' non trovato, impossibile rimuovere.")

            #self.notebook_repository.remove_doc_from_metadata() #Todo()

            return True
        except Exception as e:
            logger.error(f"Errore durante l'eliminazione del documento '{file_name}': {e}", exc_info=True)
            return False

    def list_documents(self) -> list:
        """
        Returns a list of documents associated with the notebook.
        """
        try:
            docs = self.notebook_repository.get_list_docs(self.notebook_id)
            return docs if docs else []
        except Exception as e:
            logger.error(f"Errore nel recupero lista documenti: {e}")
            return []

    def is_ready(self) -> bool:
        return self.ready and self.ingestion_layer is not None

    def close(self):

        if not self.ready:
            logger.warning("ChatManager già chiuso o non inizializzato.")
            return

        try:
            if self.last_summary:
                self.notebook_repository.update_chat_metadata(self.notebook_id, self.chat_id, summary=self.last_summary)
                logger.info(f"Ultimo summary salvato per chat {self.chat_id}")

            if self.chat_repository:
                self.chat_repository.reset_chat(self.chat_id)
                logger.info(f"Cronologia Redis pulita per chat {self.chat_id}")

        except Exception as e:
            logger.error(f"Errore durante la chiusura del ChatManager: {e}", exc_info=True)
        finally:
            self.ready = False
            self.ingestion_layer = None
            logger.info(f"ChatManager chiuso correttamente.")