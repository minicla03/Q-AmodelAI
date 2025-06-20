import os
from ingestion import setup_qa_system
from retrival import ask_question
from evaluation import evaluate_all

class QASystemManager:
    '''
    Gestisce l'inizializzazione e le operazioni del sistema di domande e risposte.
    Questa classe si occupa di configurare il sistema QA, gestire le richieste e valutare le risposte.
    '''
    def __init__(self, pdf_path="data/Android.pdf", persist_dir="chroma_db"):
        try:
            self.qa_chain = setup_qa_system(pdf_path, persist_dir)
            self.ready = True
        except Exception as e:
            print(f"[QA Init Error] {e}")
            self.qa_chain = None
            self.ready = False

    def is_ready(self):
        return self.ready

    def ask(self, query, language="italiano"):
        if not self.qa_chain:
            return "Sistema QA non pronto", []
        risposta, sources = ask_question(self.qa_chain, query, language)
        return risposta, sources

    def evaluate(self, prediction, ground_truth):
        return evaluate_all(prediction, ground_truth)
