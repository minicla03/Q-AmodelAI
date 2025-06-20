'''
Evaluation module for assessing the performance of a question-answering system.
This module provides functions to compute various evaluation metrics such as
Exact Match, F1 score, BLEU score, and ROUGE-L score.
'''

import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

TEST_CASES = [
    {
        "query": "Cosa sono i servizi in Android?",
        "expected_answer": "I servizi in Android sono componenti che permettono di eseguire operazioni in background senza interagire con l'utente."
    },
    {
        "query": "Cos'è un'activity?",
        "expected_answer": "Un'activity è una singola schermata con una interfaccia utente in un'app Android."
    },
    {
        "query": "A cosa serve il manifest.xml?",
        "expected_answer": "Il file AndroidManifest.xml fornisce informazioni essenziali al sistema sul contenuto dell'app."
    },
]

def compute_exact_match(prediction, ground_truth):
    return int(prediction.strip().lower() == ground_truth.strip().lower())

def compute_f1(prediction, ground_truth):
    pred_tokens = prediction.lower().split()
    gt_tokens = ground_truth.lower().split()
    common = set(pred_tokens) & set(gt_tokens)
    if len(common) == 0:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    return 2 * (precision * recall) / (precision + recall)

def compute_bleu(prediction, ground_truth):
    reference = [nltk.word_tokenize(ground_truth.lower())]
    hypothesis = nltk.word_tokenize(prediction.lower())
    return sentence_bleu(reference, hypothesis, smoothing_function=SmoothingFunction().method1)

def compute_rouge(prediction, ground_truth):
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(ground_truth, prediction)
    return scores['rougeL'].fmeasure

def evaluate_all(prediction, ground_truth):
    return {
        "Exact Match": compute_exact_match(prediction, ground_truth),
        "F1": compute_f1(prediction, ground_truth),
        "BLEU": compute_bleu(prediction, ground_truth),
        "ROUGE-L": compute_rouge(prediction, ground_truth),
    }
