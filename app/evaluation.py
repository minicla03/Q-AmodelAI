'''
This module provides functions to evaluate text predictions against ground truth using various metrics:
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
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

_semantic_model = None

def get_semantic_model():
    global _semantic_model
    if _semantic_model is None:
        # Modello multilingue ottimizzato per similarity
        _semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _semantic_model

def compute_f1(prediction, ground_truth, language='italian'):
    pred_tokens = word_tokenize(prediction.lower(), language=language)
    gt_tokens = word_tokenize(ground_truth.lower(), language=language)
    common = set(pred_tokens) & set(gt_tokens)
    if len(common) == 0:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    return 2 * (precision * recall) / (precision + recall)

def compute_bleu(prediction, ground_truth, language='italian'):
    reference = [word_tokenize(ground_truth.lower(), language=language)]
    hypothesis = word_tokenize(prediction.lower(), language=language)
    return sentence_bleu(reference, hypothesis, smoothing_function=SmoothingFunction().method1)

def compute_rouge(prediction, ground_truth):
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(ground_truth, prediction)
    return scores['rougeL'].fmeasure

def compute_context_precision_recall(retrieved_docs, relevant_docs):
    retrieved_set = set(retrieved_docs)
    relevant_set = set(relevant_docs)
    true_positives = len(retrieved_set & relevant_set)
    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
    recall = true_positives / len(relevant_set) if relevant_set else 0.0
    return precision, recall

def compute_semantic_similarity(prediction, ground_truth):
    model = get_semantic_model()
    embeddings = model.encode([prediction, ground_truth])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return max(0.0, min(1.0, similarity))
    
def evaluate_all(prediction, ground_truth, language='italian'):
    return {
        "F1": compute_f1(prediction, ground_truth, language=language),
        "BLEU": compute_bleu(prediction, ground_truth, language=language),
        "ROUGE-L": compute_rouge(prediction, ground_truth),
        "Semantic Similarity": compute_semantic_similarity(prediction, ground_truth),

    }
