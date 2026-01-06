from deepeval.metrics import SummarizationMetric, HallucinationMetric, FaithfulnessMetric
from deepeval.models import OllamaModel

assessment_questions = [
    # Accuratezza / Precision
    "Il riassunto riporta correttamente i fatti principali della conversazione?",
    "Ci sono affermazioni nel riassunto che non compaiono nella conversazione?",
    "Il riassunto evita interpretazioni o distorsioni dei messaggi originali?",
    "Le informazioni riportate sono coerenti con il contenuto della conversazione?",

    # Completezza / Coverage
    "Tutti i temi principali della conversazione sono inclusi nel riassunto?",
    "Sono stati omessi punti critici o importanti?",
    "Il riassunto cattura correttamente le richieste e risposte chiave?",
    "Le informazioni secondarie o irrilevanti sono state ridotte senza perdere contenuto utile?",

    # Coerenza e chiarezza
    "Il riassunto è scorrevole e facile da leggere?",
    "La sequenza delle informazioni ha senso e segue la conversazione?",
    "Ci sono contraddizioni o incoerenze interne nel riassunto?",
    "Il linguaggio usato è chiaro e non ambiguo?",

    # Rilevanza e utilità
    "Il riassunto permette di comprendere la conversazione senza leggerla tutta?",
    "Le informazioni riportate sono rilevanti rispetto all'obiettivo del riassunto?",
    "Il riassunto evidenzia le decisioni o azioni principali emerse dalla conversazione?",
    "Il riassunto può essere usato come riferimento affidabile per chi non ha letto la conversazione?",

    # Ragionamento / motivazione
    "Eventuali conclusioni presenti nel riassunto sono supportate dai dati della conversazione?",
    "Il riassunto esplicita motivazioni o contesto quando necessario?",
    "Il riassunto evita inferenze non supportate dai messaggi originali?",
    "Il riassunto sintetizza correttamente i punti chiave senza aggiungere contenuto inventato?"
]

def get_list_deep_eval_metrics():

    ollama_model = OllamaModel(model="gpt-oss:120b-cloud")#, api_key=os.getenv("OLLAMA_API_KEY"))

    return [
        SummarizationMetric(
            verbose_mode=True,
            assessment_questions=assessment_questions,
            n=20,
            model=ollama_model,
            truths_extraction_limit=20,
            include_reason=True
        ),
        HallucinationMetric(
            verbose_mode=True,
            include_reason=True,
            model=ollama_model,
        ),
        FaithfulnessMetric(
            threshold=0.7,
            include_reason=True,
            model=ollama_model,
        )
    ]

from rouge_score import rouge_scorer
import bert_score
import textstat

def classic_metric(reference_summary: str, generated_summary: str):
    # ROUGE
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    rouge_scores = scorer.score(reference_summary, generated_summary)
    rouge_dict = {k: {"precision": v.precision, "recall": v.recall, "fmeasure": v.fmeasure} for k, v in rouge_scores.items()}

    # BERTScore
    P, R, F1 = bert_score.score([generated_summary], [reference_summary], lang="it", model_type="bert-base-multilingual-cased")
    bert_dict = {"precision": float(P.mean()), "recall": float(R.mean()), "f1": float(F1.mean())}

    # Leggibilità
    readability_score = textstat.flesch_reading_ease(generated_summary)

    # Restituisci tutto in un dizionario
    return {
        "rouge": rouge_dict,
        "bertscore": bert_dict,
        "readability": readability_score
    }

# Esempio d'uso
reference = "The cat sat on the mat."
generated = "The cat is on the mat."
metrics = classic_metric(reference, generated)
print(metrics)
