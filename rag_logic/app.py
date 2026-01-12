import logging
import sys
import time
import uuid

from dotenv import load_dotenv

load_dotenv(override=True)

from persistence.long_term_memory.mongo.MongoDBMS import MongoConnectionManager
from persistence.short_term_memory.redis.RedisDBMS import RedisConnectionManager
from rag_logic.memory.NotebookManger import NotebookManager
from rag_logic.memory.ChatManager import ChatManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("RAG_Flow_CLI")

def check_db_connections():
    """Verifica preliminare delle connessioni ai DB."""
    try:
        MongoConnectionManager.instance()
        RedisConnectionManager.instance()
        logger.info("Connessione ai Database (Mongo/Redis) verificata con successo.")
        return True
    except Exception as e:
        logger.critical(f"Errore critico connessione DB: {e}")
        return False


def retrieve_active_chat(redis_manager, notebook_id: str) -> str:
    r = redis_manager.client
    redis_key = f"chat_ref:{notebook_id}"

    existing_id = r.get(redis_key)
    if existing_id:
        logger.info(f"Trovata sessione attiva su Redis: {existing_id.decode('utf-8')}")
        return existing_id.decode('utf-8')

    new_id = str(uuid.uuid4())
    logger.info(f"Nessuna sessione attiva. Creata nuova chat_id: {new_id}")
    return new_id


def select_existing_notebook(nb_manager, user_id):
    notebooks = nb_manager.retrieve_notebook_by_user(user_id)

    if not notebooks:
        print(" >> Nessun notebook trovato per questo utente.")
        return None

    print("\n--- Notebook Disponibili ---")
    for idx, nb in enumerate(notebooks):
        # Gestione ibrida dict/object per compatibilità
        if isinstance(nb, dict):
            n_name = nb.get('notebook_name', 'No Name')
            n_id = nb.get('id_notebook') or nb.get('_id')
        else:
            n_name = getattr(nb, 'notebook_name', 'No Name')
            n_id = getattr(nb, 'id_notebook', None)

        print(f" [{idx + 1}] {n_name} (ID: {n_id})")
    print("----------------------------")

    while True:
        choice = input("Seleziona numero (#) o 'n' per nuovo: ").strip()
        if choice.lower() == 'n':
            return None

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(notebooks):
                return notebooks[idx]
        print("Scelta non valida.")


def main():
    print("==========================================")
    print("      RAG SYSTEM CLI INTERFACE v2         ")
    print("==========================================\n")

    if not check_db_connections():
        return

    USER_ID = "developer_user_01"
    DOCS_PATH = "./docs_storage"

    try:
        logger.info("Inizializzazione Manager...")
        nb_manager = NotebookManager()
        redis_manager = RedisConnectionManager.instance()

        print(f"Utente: {USER_ID}")
        print("[1] Crea Nuovo Notebook")
        print("[2] Apri Notebook Esistente")

        mode = input("> ").strip()

        mongo_id = None
        chat_id = None
        notebook_obj = None
        notebook_name = "Untitled"

        # --- FASE 1: Selezione Notebook ---
        if mode == "2":
            notebook_obj = select_existing_notebook(nb_manager, USER_ID)

        if notebook_obj:
            if isinstance(notebook_obj, dict):
                mongo_id = notebook_obj.get('id_notebook') or notebook_obj.get('_id')
                notebook_name = notebook_obj.get('notebook_name')
            else:
                mongo_id = getattr(notebook_obj, 'id_notebook', None)
                notebook_name = getattr(notebook_obj, 'notebook_name', "Untitled")

            chat_id = retrieve_active_chat(redis_manager, str(mongo_id))
            print(f"\n>> Riapertura Notebook: '{notebook_name}'")

        else:
            if mode == "2": print("Creazione nuovo notebook (fallback)...")
            notebook_name = input("Inserisci nome per il nuovo notebook: ").strip() or "Untitled_NB"

            notebook_obj, chat_id = nb_manager.create_notebook(notebook_name, USER_ID)
            mongo_id = notebook_obj.id_notebook
            print(f"\n>> Nuovo Notebook creato: '{notebook_name}'")

        print(f">> MongoID: {mongo_id} | ChatID: {chat_id}")

        # --- FASE 2: Istanziazione ChatManager ---
        manager = ChatManager(
            user_id=USER_ID,
            notebook_id=mongo_id,
            chat_id=chat_id,
            document_path=DOCS_PATH
        )

        print("\n=== Sistema Pronto. Comandi disponibili: ===")
        print(" - Scrivi una domanda per attivare la RAG.")
        print(" - /add <path_file>  : Aggiunge un documento.")
        print(" - /list             : Elenca i documenti.")
        print(" - /del <filename>   : Elimina un documento.")
        print(" - /flashcards       : Lista flashcard (RAM + DB).")
        print(" - /del_fc <id>      : Elimina flashcard.")
        print(" - /quiz             : Lista quiz (RAM + DB).")
        print(" - /del_quiz <id>    : Elimina quiz.")
        print(" - /exit             : Chiude sessione e SALVA su DB.")
        print(" - /save             : Salva buffer (Flashcard/Quiz) su DB.")
        print("============================================\n")

        # --- FASE 3: Loop Interattivo ---
        while True:
            try:
                user_input = input(f"({notebook_name}) > ").strip()

                if not user_input:
                    continue

                # === COMANDO EXIT ===
                if user_input.lower() in ["/exit", "exit", "quit"]:
                    print("Salvataggio stato e chiusura...")
                    manager.close()  # Questo ora salva flashcard/quiz in RAM su DB
                    print("Sessione terminata.")
                    break

                # === COMANDO SAVE (NUOVO) ===
                elif user_input.lower() == "/save":
                    # Assumiamo che ChatManager esponga un metodo save o accediamo ai manager interni
                    # Opzione A (se hai implementato save_all in ChatManager):
                    # manager.save_all()

                    # Opzione B (Accesso diretto ai manager interni se pubblici):
                    saved_fc = manager.flashcard_manager.persist_buffer()
                    saved_qz = manager.quiz_manager.persist_buffer()
                    print(f" >> Salvataggio completato: {saved_fc} Flashcards, {saved_qz} Quiz salvati su DB.")

                # === GESTIONE DOCUMENTI ===
                elif user_input.lower().startswith("/add "):
                    file_path = user_input[5:].strip().replace('"', '').replace("'", "")
                    manager.add_document(file_path)

                elif user_input.lower() == "/list":
                    docs = manager.list_documents()
                    print(f"Documenti indicizzati ({len(docs)}):")
                    for d in docs:
                        # Gestione stringa o dict
                        d_name = d if isinstance(d, str) else d.get('filename', str(d))
                        print(f" - {d_name}")

                elif user_input.lower().startswith("/del "):
                    filename = user_input[5:].strip()
                    success = manager.delete_document(filename)
                    print(f"Eliminazione '{filename}': {'COMPLETATA' if success else 'FALLITA'}")

                # === GESTIONE FLASHCARDS ===
                elif user_input.lower() == "/flashcards":
                    fcs = manager.get_stored_flashcards()
                    print(f"\n--- Flashcards ({len(fcs)}) ---")
                    for fc in fcs:
                        status = "[UNSAVED RAM]" if fc.get('is_unsaved') else "[SAVED DB]"
                        f_id = fc.get('_id', 'N/A')
                        q_text = fc.get('question', 'N/A')
                        print(f"{status} ID: {f_id} | Q: {q_text[:50]}...")

                elif user_input.lower().startswith("/del_fc "):
                    fc_id = user_input[8:].strip()
                    if manager.delete_stored_flashcard(fc_id):
                        print(f"Flashcard {fc_id} eliminata.")
                    else:
                        print("Errore: ID non trovato.")

                # === GESTIONE QUIZ ===
                elif user_input.lower() == "/quiz":
                    qz_list = manager.get_stored_quizzes()
                    print(f"\n--- Quiz ({len(qz_list)}) ---")
                    for q in qz_list:
                        status = "[UNSAVED RAM]" if q.get('is_unsaved') else "[SAVED DB]"
                        q_id = q.get('_id', 'N/A')

                        q_text = q.get('question', 'N/A')
                        print(f"{status} ID: {q_id} | Q: {q_text[:50]}...")

                elif user_input.lower().startswith("/del_quiz "):
                    q_id = user_input[10:].strip()
                    if manager.delete_stored_quiz(q_id):
                        print(f"Quiz {q_id} eliminato.")
                    else:
                        print("Errore: ID non trovato.")

                # === RAG PIPELINE ===
                else:
                    start_time = time.time()
                    response = manager.execute_rag_pipeline(
                        user_query=user_input,
                        memory_ability=True,
                    )
                    elapsed = time.time() - start_time

                    if response.get("error"):
                        print(f"\n[SYSTEM ERROR]: {response['error']}")
                        if response.get("traceback"):
                            logger.debug(response['traceback'])
                    else:
                        ai_text = response.get("ai_response", "Nessuna risposta.")
                        print(f"\n(AI) > {ai_text}")

                        if response.get("type") == "QA" and "docs_source" in response:
                            explanation = response.get("docs_source")
                            print(f"[Explanation] \n Sources used: {len(explanation)}")
                            for result in explanation:
                                print(f"\nDocument {result['rank']} (Confidence: {result['confidence_level']})")
                                print(f"   Source: Page {result['metadata']['page_number']}")
                                print(f"   Score: {result['score']:.3f}")
                                print(f"   Reason: {result['explanation_text']}")
                                print(f"   Keywords: {result['key_terms']}")

                        if "flashcard" in ai_text.lower() and "buffer" in ai_text.lower():
                            print(" [!] Nuove flashcard in memoria. Usa /flashcards per vederle.")

                        print(f"       [Time: {elapsed:.2f}s]")

            except KeyboardInterrupt:
                print("\nInterruzione forzata (CTRL+C).")
                manager.close()
                break

    except Exception as e:
        logger.critical(f"Errore irreversibile nel main loop: {e}", exc_info=True)
        try:
            manager.close()
        except:
            pass


if __name__ == "__main__":
    main()