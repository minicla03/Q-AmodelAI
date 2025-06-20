'''
This module provides functions to evaluate text predictions against ground truth using various metrics:
- Exact Match
- F1 Score
- BLEU Score
'''

from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def compute_exact_match(prediction, ground_truth):
    return int(prediction.strip().lower() == ground_truth.strip().lower())


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


def evaluate_all(prediction, ground_truth, language='italian'):
    return {
        "Exact Match": compute_exact_match(prediction, ground_truth,),
        "F1": compute_f1(prediction, ground_truth, language=language),
        "BLEU": compute_bleu(prediction, ground_truth, language=language),
        "ROUGE-L": compute_rouge(prediction, ground_truth),
    }
