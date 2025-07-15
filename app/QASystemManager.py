import os
import shutil
from retrival import ask_question
from ingestion import setup_qa_system, add_document_to_vectorstore, delete_document_from_vectorstore

class QASystemManager:
    '''
    Gestisce l'inizializzazione e le operazioni del sistema di domande e risposte.
    Questa classe si occupa di configurare il sistema QA, gestire le richieste e valutare le risposte.
    '''
    def __init__(self, pdf_path="data", persist_dir="chroma_db"):
        self.pdf_path = pdf_path
        self.persist_dir = persist_dir
        self.ready = False
        self.qa_chain = None
        self._initialize()

    def _initialize(self, force_rebuild=False):
        try:
            self.qa_chain = setup_qa_system(self.pdf_path, self.persist_dir, force_rebuild=force_rebuild)
            self.ready = True
        except Exception as e:
            print(f"[QA Init Error] {e}")
            self.qa_chain = None
            self.ready = False

    def is_ready(self):
        return self.ready

    def ask(self, query, language="italian"):
        if not self.qa_chain:
            return "Sistema QA non pronto", []
        return ask_question(self.qa_chain, query, language)

    def add_document(self, file_path):
        """
        Aggiunge un nuovo documento PDF al vectorstore esistente.
        """
        print(f"[DEBUG] Aggiunta documento: {file_path}")
        
        dest_path = os.path.join(self.pdf_path, os.path.basename(file_path))
        if not os.path.exists(dest_path):
            shutil.copy(file_path, dest_path)
        print(f"[DEBUG] Documento copiato in: {dest_path}")

        try:
            add_document_to_vectorstore(file_path, persist_dir=self.persist_dir)
            print(f"[DEBUG] Documento aggiunto al vectorstore con successo")
        except Exception as e:
            print(f"[ERROR] Errore durante l'aggiunta al vectorstore: {e}")
            return

        self.close()
        self._initialize(force_rebuild=False)

    def close(self):
        if self.qa_chain:
            self.qa_chain = None
    
    def list_documents(self):
        """
        Restituisce una lista dei documenti PDF attualmente presenti nella directory `pdf_path`.
        """
        try:
            return sorted([
                f for f in os.listdir(self.pdf_path)
                if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(self.pdf_path, f))
            ])
        except Exception as e:
            print(f"[ERROR] Impossibile elencare i documenti: {e}")
            return []
        
    def delete_document(self, file_name):
        """
        Elimina un documento PDF dalla directory e i suoi chunk dal vectorstore.
        
        Args:
            file_name (str): Il nome del file (es. "Android.pdf") da eliminare.
        """
        file_path = os.path.join(self.pdf_path, file_name)
        
        if not os.path.exists(file_path):
            print(f"[ERROR] Il documento '{file_name}' non esiste nella directory dei PDF.")
            return False

        print(f"[DEBUG] Eliminazione documento: {file_path}")
        try:
            # 1. Elimina i chunk dal vectorstore
            delete_document_from_vectorstore(file_name, persist_dir=self.persist_dir)
            os.remove(file_path)
            print(f"[DEBUG] Documento '{file_name}' eliminato fisicamente.")
            
            self.close()
            self._initialize(force_rebuild=False)
            print(f"[DEBUG] QA System ricaricato dopo l'eliminazione.")
            return True
        except Exception as e:
            print(f"[ERROR] Errore durante l'eliminazione del documento: {e}")
            return False


