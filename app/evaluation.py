'''
Questo modulo contiene funzioni per valutare le prestazioni di un sistema di domande e risposte.
Le metriche calcolate includono:
- Exact Match
- F1 Score
- BLEU Score
- ROUGE-L
- Context Precision
- Context Recall
'''

from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

_semantic_model = None

def get_semantic_model():
    global _semantic_model
    if _semantic_model is None:
        _semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _semantic_model

def compute_f1(prediction, ground_truth, language='italian'):
    '''
    Calcola l'F1 Score tra la previsione e la risposta attesa.
    L'F1 Score è la media armonica tra precision e recall:
    - Precision: frazione di token predetti corretti
    - Recall: frazione di token di riferimento catturati
    Utilizza il tokenization per gestire le differenze linguistiche.
    Args:
        prediction (str): La risposta generata dal modello.
        ground_truth (str): La risposta corretta attesa.
        language (str): La lingua della risposta, usata per la tokenizzazione.
    Returns:
        float: L'F1 Score calcolato tra la previsione e la risposta attesa.
    '''
    pred_tokens = word_tokenize(prediction.lower(), language=language)
    gt_tokens = word_tokenize(ground_truth.lower(), language=language)
    common = set(pred_tokens) & set(gt_tokens)
    if len(common) == 0:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    return 2 * (precision * recall) / (precision + recall)

def compute_bleu(prediction, ground_truth, language='italian'):
    '''
    Calcola il BLEU Score tra la previsione e la risposta attesa.
    Misura la precisione n-gram tra predizione e riferimento
    - Penalizza risposte troppo brevi
    - Tiene conto della posizione delle parole
    - Smoothing per evitare punteggi zero
    Args:
        prediction (str): La risposta generata dal modello.
        ground_truth (str): La risposta corretta attesa.
        language (str): La lingua della risposta, usata per la tokenizzazione.
    Returns:
        float: Il BLEU Score calcolato tra la previsione e la risposta attesa.
    '''
    reference = [word_tokenize(ground_truth.lower(), language=language)]
    hypothesis = word_tokenize(prediction.lower(), language=language)
    return sentence_bleu(reference, hypothesis, smoothing_function=SmoothingFunction().method1)

def compute_rouge(prediction, ground_truth):
    '''
    Calcola il ROUGE-L Score tra la previsione e la risposta attesa.
    Misura la corrispondenza della sequenza più lunga comune:
    - Considera l'ordine delle parole
    - Meno sensibile a riarrangiamenti che BLEU
    - Particolarmente utile per riassunti
    Args:
        prediction (str): La risposta generata dal modello.
        ground_truth (str): La risposta corretta attesa.
    Returns:
        float: Il ROUGE-L Score calcolato tra la previsione e la risposta attesa.
    '''
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(ground_truth, prediction)
    return scores['rougeL'].fmeasure

def compute_context_precision_recall(retrieved_docs, relevant_docs):
    '''
    Calcola precisione e recall del contesto recuperato.
    Precisione: frazione di documenti recuperati effettivamente rilevanti
    Recall: frazione di documenti rilevanti effettivamente recuperati
    Args:
        retrieved_docs (list): Lista dei documenti recuperati dal sistema.
        relevant_docs (list): Lista dei documenti rilevanti attesi.
    Returns:
        tuple: (precision, recall) calcolati tra i documenti recuperati e quelli rilevanti.
    '''
    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)
    true_positives = len(retrieved_set & relevant_set)
    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
    recall = true_positives / len(relevant_set) if relevant_set else 0.0
    return precision, recall

def compute_semantic_similarity(prediction, ground_truth):
    '''
    Calcola similarità semantica tra predizione e riferimento
    Utilizza embeddings di frasi e cosine similarity:
    - Cattura similarità di significato oltre la forma lessicale
    - Modello multilingue permette confronti cross-lingua
    - Valore tra 0 (nessuna similarità) e 1 (identico)
    Args:
        prediction (str): La risposta generata dal modello.
        ground_truth (str): La risposta corretta attesa.
    Returns:
        float: La similarità semantica calcolata tra la previsione e la risposta attesa.
    '''
    model = get_semantic_model()
    embeddings = model.encode([prediction, ground_truth])
    similarity = cosine_similarity(np.array([embeddings[0]]), np.array([embeddings[1]]))[0][0]
    return max(0.0, min(1.0, similarity))
    
def evaluate_all(prediction, ground_truth, language='italian'):
    return {
        "F1": compute_f1(prediction, ground_truth, language=language),
        "BLEU": compute_bleu(prediction, ground_truth, language=language),
        "ROUGE-L": compute_rouge(prediction, ground_truth),
        "Semantic Similarity": compute_semantic_similarity(prediction, ground_truth),
    }
