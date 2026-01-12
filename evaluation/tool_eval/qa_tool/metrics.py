from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")


def compute_f1(prediction, ground_truth):
    """
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
    """
    pred_tokens = tokenizer.tokenize(prediction.lower())
    gt_tokens = tokenizer.tokenize(ground_truth.lower())
    common = set(pred_tokens) & set(gt_tokens)
    if len(common) == 0:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    return 2 * (precision * recall) / (precision + recall)

def compute_bleu(prediction, ground_truth):
    """
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
    """
    reference = [tokenizer.tokenize(ground_truth.lower())]
    hypothesis = tokenizer.tokenize(prediction.lower())
    smooth = SmoothingFunction().method1
    return sentence_bleu(reference, hypothesis, smoothing_function=smooth)

def compute_rouge(prediction, ground_truth):
    """
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
    """
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(ground_truth, prediction)
    return scores['rougeL'].fmeasure

def extract_retrieved_doc_ids(raw_sources):
    doc_ids = []
    for item in raw_sources:
        if isinstance(item, dict):
            meta = item.get("metadata", {})
            if "source" in meta:
                doc_ids.append(meta["source"])
            elif "doc_id" in meta:
                doc_ids.append(meta["doc_id"])
        else:
            if hasattr(item, "metadata"):
                doc_ids.append(
                    item.metadata.get("source") or item.metadata.get("doc_id")
                )
    return [d for d in doc_ids if d is not None]

def precision_recall_at_k(retrieved_ids, relevant_ids, k):
    retrieved_k = retrieved_ids[:k]
    relevant_set = set(relevant_ids)

    true_positives = len(set(retrieved_k) & relevant_set)

    precision = true_positives / len(retrieved_k) if retrieved_k else 0.0
    recall = true_positives / len(relevant_set) if relevant_set else 0.0

    return precision, recall

def mean_reciprocal_rank(retrieved_ids, relevant_ids):
    relevant_set = set(relevant_ids)
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_set:
            return 1.0 / rank
    return 0.0
    
def custom_metrics(prediction, ground_truth):
    return {
        "F1": compute_f1(prediction, ground_truth),
        "BLEU": compute_bleu(prediction, ground_truth),
        "ROUGE-L": compute_rouge(prediction, ground_truth),
    }

def calculate_retrieval_metrics(retrieved_ids, relevant_ids, k):
    return {
        f"precision_recall_at_{k}": precision_recall_at_k(retrieved_ids, relevant_ids, k),
        "mean_reciprocal_rank": mean_reciprocal_rank(retrieved_ids, relevant_ids),
    }