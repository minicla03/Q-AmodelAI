"""
Modulo per la valutazione di risposte generate da sistemi QA

Fornisce metriche per valutare la qualità di predizioni di testo rispetto a risposte di riferimento:
- Metriche basate su corrispondenza esatta e sovrapposizione lessicale
- Metriche basate su similarità semantica
- Metriche per valutare la rilevanza del contesto recuperato
"""

from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# Download risorse NLTK se mancanti
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Cache per il modello di similarità semantica
_semantic_model = None

"""
Inizializza e restituisce il modello per similarità semantica (Singleton pattern)
  
Utilizza un modello multilingue leggero ma efficace per embeddings di frasi
Modello scelto: 'paraphrase-multilingual-MiniLM-L12-v2' di SentenceTransformers
"""
def get_semantic_model():

    global _semantic_model
    if _semantic_model is None:
        _semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _semantic_model


"""
Calcola l'F1 Score tra predizione e riferimento
   
L'F1 Score è la media armonica tra precision e recall:
    - Precision: frazione di token predetti corretti
    - Recall: frazione di token di riferimento catturati
    
Valore tra 0 (peggiore) e 1 (migliore)
Utile per valutare l'accuratezza lessicale
"""
def compute_f1(prediction, ground_truth, language='italian'):

    pred_tokens = word_tokenize(prediction.lower(), language=language)
    gt_tokens = word_tokenize(ground_truth.lower(), language=language)
    common = set(pred_tokens) & set(gt_tokens)
    if len(common) == 0:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    return 2 * (precision * recall) / (precision + recall)

"""
Calcola il BLEU score per valutare la qualità della traduzione/risposta
   
Misura la precisione n-gram tra predizione e riferimento
    - Penalizza risposte troppo brevi
    - Tiene conto della posizione delle parole
    - Smoothing per evitare punteggi zero
    
Valore tra 0 (peggiore) e 1 (migliore)
"""
def compute_bleu(prediction, ground_truth, language='italian'):

    reference = [word_tokenize(ground_truth.lower(), language=language)]
    hypothesis = word_tokenize(prediction.lower(), language=language)
    return sentence_bleu(reference, hypothesis, smoothing_function=SmoothingFunction().method1)

"""
Calcola ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation)
    
Misura la corrispondenza della sequenza più lunga comune:
    - Considera l'ordine delle parole
    - Meno sensibile a riarrangiamenti che BLEU
    - Particolarmente utile per riassunti
    
Valore tra 0 (peggiore) e 1 (migliore)
"""
def compute_rouge(prediction, ground_truth):

    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(ground_truth, prediction)
    return scores['rougeL'].fmeasure

"""
Calcola precisione e recall del contesto recuperato
    
Precisione: frazione di documenti recuperati effettivamente rilevanti
Recall: frazione di documenti rilevanti effettivamente recuperati
    
Metriche fondamentali per valutare la qualità del retrieval
"""
def compute_context_precision_recall(retrieved_docs, relevant_docs):

    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)
    true_positives = len(retrieved_set & relevant_set)
    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
    recall = true_positives / len(relevant_set) if relevant_set else 0.0
    return precision, recall

"""
Calcola similarità semantica tra predizione e riferimento
    
Utilizza embeddings di frasi e cosine similarity:
    - Cattura similarità di significato oltre la forma lessicale
    - Modello multilingue permette confronti cross-lingua
    - Valore tra 0 (nessuna similarità) e 1 (identico)
"""
def compute_semantic_similarity(prediction, ground_truth):

    model = get_semantic_model()
    embeddings = model.encode([prediction, ground_truth])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return max(0.0, min(1.0, similarity))

"""
Esegue tutte le valutazioni e restituisce un report completo
    
Combina metriche:
    - Lessicali (F1, BLEU, ROUGE)
    - Semantiche (cosine similarity)
    
Ideale per valutazioni end-to-end di sistemi QA
"""  
def evaluate_all(prediction, ground_truth, language='italian'):
    
    return {
        "F1": compute_f1(prediction, ground_truth, language=language),
        "BLEU": compute_bleu(prediction, ground_truth, language=language),
        "ROUGE-L": compute_rouge(prediction, ground_truth),
        "Semantic Similarity": compute_semantic_similarity(prediction, ground_truth),
    }