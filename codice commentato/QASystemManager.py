import os
import shutil 
from retrival import ask_question  
from ingestion import setup_qa_system, add_document_to_vectorstore 

"""
Gestisce l'inizializzazione e le operazioni del sistema di domande e risposte.

Questa classe si occupa di:
    - Configurare il sistema QA
    - Gestire le richieste degli utenti
    - Valutare le risposte
    - Gestire l'aggiunta di nuovi documenti
"""

class QASystemManager:
    #  Inizializza il gestore del sistema QA.
    def __init__(self, pdf_path = "data", persist_dir = "chroma_db"):
        self.pdf_path = pdf_path  # Cartella dove vengono salvati i PDF
        self.persist_dir = persist_dir  # Cartella del database vettoriale
        self.ready = False  # Flag che indica se il sistema è pronto
        self.qa_chain = None  # Oggetto che rappresenta la catena QA
        self._initialize()  # Chiamata all'inizializzazione interna

    # Inizializza il sistema QA.
    def _initialize(self, force_rebuild=False):
        try:
            # Configura il sistema QA con i percorsi specificati
            self.qa_chain = setup_qa_system(self.pdf_path, self.persist_dir, force_rebuild=force_rebuild)
            self.ready = True  # Sistema pronto
        except Exception as e:
            print(f"[QA Init Error] {e}")  # Stampa l'errore
            self.qa_chain = None
            self.ready = False  # Sistema non pronto

    # Verifica se il sistema QA è pronto per rispondere alle domande.
    def is_ready(self):
        return self.ready
    
    # Invia una domanda al sistema QA.
    def ask(self, query, language="italian"):
        if not self.qa_chain:
            return "Sistema QA non pronto", []  # Messaggio di errore
        return ask_question(self.qa_chain, query, language)  # Delegata la domanda al modulo retrival
    
    # Aggiunge un nuovo documento PDF al sistema QA.
    """ Steps:
            1. Copia il file nella cartella pdf_path
            2. Aggiunge il documento al vectorstore
            3. Reinizializza il sistema QA
    """
    def add_document(self, file_path):
        print(f"[DEBUG] Aggiunta documento: {file_path}")
        
        # Costruisce il percorso di destinazione
        dest_path = os.path.join(self.pdf_path, os.path.basename(file_path))
        
        # Copia il file solo se non esiste già nella cartella
        if not os.path.exists(dest_path):
            shutil.copy(file_path, dest_path)
        print(f"[DEBUG] Documento copiato in: {dest_path}")
        try:
            # 2. Aggiunge il documento al database vettoriale
            add_document_to_vectorstore(file_path, persist_dir=self.persist_dir)
            print(f"[DEBUG] Documento aggiunto al vectorstore con successo")
        except Exception as e:
            print(f"[ERROR] Errore durante l'aggiunta al vectorstore: {e}")
            return

        # 3. Riavvia il sistema QA per includere il nuovo documento
        self.close()
        self._initialize(force_rebuild=False)

    # Chiude il sistema QA, rilasciando le risorse.    
    def close(self):
        if self.qa_chain:
            self.qa_chain = None  # Elimina la catena QA
    
    # Restituisce la lista dei documenti PDF disponibili nel sistema.
    def list_documents(self):
        try:
            # Lista tutti i file PDF nella cartella, ordinati alfabeticamente
            return sorted([
                f for f in os.listdir(self.pdf_path)
                if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(self.pdf_path, f))
            ])
        except Exception as e:
            print(f"[ERROR] Impossibile elencare i documenti: {e}")
            return []  # Restituisce lista vuota in caso di errore