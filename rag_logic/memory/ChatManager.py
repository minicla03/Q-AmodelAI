import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

from persistence.long_term_memory.mongo.MongoDBMS import MongoConnectionManager
from persistence.long_term_memory.mongo.NotebookRepository import MongoNotebookRepository
from persistence.long_term_memory.mongo.FlashRepository import MongoFlashRepository
from persistence.long_term_memory.mongo.QuizRepository import MongoQuizRepository

from rag_logic.memory.DocumentManager import DocumentManager
from rag_logic.memory.FlashcardManger import FlashcardManager
from rag_logic.memory.QuizManager import QuizManager
from rag_logic.utils import  detect_language_from_query

from rag_logic.agents.routing_agent import router_agent
from rag_logic.agents.summarizer_agent import summary_agent

from rag_logic.tools.ITool import ContextFactory

from persistence.IxRepository import IRepos
from persistence.short_term_memory.redis.RedisDBMS import RedisConnectionManager
from persistence.short_term_memory.redis.ChatRepository import ChatRepository

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
            document_path: str = "docs"
    ):

        self.user_id = user_id
        self.notebook_id = notebook_id
        self.chat_id = chat_id
        self.document_path = document_path
        mongo_conn = MongoConnectionManager.instance().db

        # Iniezione delle dipendenze
        notebook_repository: IRepos.INotebookRepository = MongoNotebookRepository(mongo_conn)
        self.chat_repository: IRepos.IChatRepository = ChatRepository(RedisConnectionManager.instance().client)
        flashcard_repository: IRepos.IFlashcardRepository = MongoFlashRepository(mongo_conn)
        quiz_repository: IRepos.IQuizRepository = MongoQuizRepository(mongo_conn)

        self.doc_manager = DocumentManager(notebook_repository, notebook_id, chat_id, document_path)
        self.flashcard_manager = FlashcardManager(flashcard_repository, notebook_id, user_id)
        self.quiz_manager = QuizManager(quiz_repository, notebook_id, user_id)

        self.notebook_repository = notebook_repository

        self.last_summary = ""
        self.ready = True

        try:
            self.last_summary = self.notebook_repository.get_last_summary(self.chat_id) or ""
        except Exception as e:
            logger.error(f"Errore init summary: {e}")

    def _restart(self):
        self.doc_manager.reload_ingestion()
        self.ready = True

    def close(self):

        if not self.ready:
            logger.warning("ChatManager già chiuso o non inizializzato.")
            return


        logger.info("Avvio procedura di chiusura sessione...")

        try:
            fc_saved = self.flashcard_manager.persist_buffer()
            if fc_saved: logger.info(f"Salvate {fc_saved} flashcard.")

            quiz_saved = self.quiz_manager.persist_buffer()
            if quiz_saved: logger.info(f"Salvate {quiz_saved} quiz.")

            if self.last_summary:
                self.notebook_repository.update_chat_metadata(
                    self.notebook_id, self.chat_id, summary=self.last_summary
                )

            if self.chat_repository:
                self.chat_repository.reset_chat(self.chat_id)

        except Exception as e:
            logger.error(f"Errore in chiusura: {e}", exc_info=True)
        finally:
            self.ready = False
            logger.info("Sessione chiusa.")

    def execute_rag_pipeline(self, user_query, default_language="italian", memory_ability=True, toon_format=False):

        logger.info("Avvio pipeline RAG per query utente: %s", user_query)

        language = detect_language_from_query(user_query) or default_language
        logger.info("Lingua rilevata: %s", language)

        tool_name = router_agent(user_query, language)
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
            response = context.execute(
                self.doc_manager.retriever,
                query,
                language,
                toon_format=toon_format
            )

            self._update_memory(tool_name, user_query, response)
            logger.info("Esecuzione completata con successo.")
            return response
        except Exception as e:
            logger.error(f"RAG Error: {e}", exc_info=True)
            return {"error": str(e), "ai_response": None}

    def _update_memory(self, tool_name, user_query, response):

        if tool_name == "QA_TOOL":
            self.chat_repository.add_message(self.chat_id, {"type": "human", "mex": user_query})
            logger.info("User message added to chat history.")
            ai_text_response = response.get("ai_response", "Contenuto generato.")
            self.chat_repository.add_message(self.chat_id, {"type": "ai", "mex": ai_text_response})
            logger.info("AI response saved to chat history.")
        elif tool_name == "FLASHCARD_TOOL":
            flashcards = response.get("result", [])
            if flashcards:
                self.flashcard_manager.add_to_buffer(flashcards)
                logger.info(f"Ho generato {len(flashcards)} flashcard (buffer).")
        elif tool_name == "QUIZ_TOOL":
            quiz = response.get("result")
            if quiz:
                self.quiz_manager.add_to_buffer(quiz)
                ai_text = "Ho generato un nuovo quiz (buffer)."

    # Docs
    def add_document(self, path):
        return self.doc_manager.add_document(path)

    def delete_document(self, name):
        return self.doc_manager.delete_document(name)

    def list_documents(self):
        return self.doc_manager.list_documents()

    # Flashcards
    def get_stored_flashcards(self):
        return self.flashcard_manager.get_all()

    def delete_stored_flashcard(self, fid):
        return self.flashcard_manager.delete(fid)

    # Quiz
    def get_stored_quizzes(self):
        return self.quiz_manager.get_all()

    def delete_stored_quiz(self, qid):
        return self.quiz_manager.delete(qid)