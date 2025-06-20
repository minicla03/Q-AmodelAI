from QASystemManager import QASystemManager
from evaluation import evaluate_all

manager = QASystemManager()

if not manager.is_ready():
    print("QA System non pronto.")
    exit()

print("Inizio valutazione su test set...\n")

results = []

TEST_CASES = [
    {
        "query": "Cosa sono i servizi in Android?",
        "expected_answer": "I servizi in Android sono componenti che permettono di eseguire operazioni in background senza interagire con l'utente.",
        "language_hint": "italian"
    },
    {
        "query": "Cos'è un'activity?",
        "expected_answer": "Un'activity è una singola schermata con una interfaccia utente in un'app Android.",
        "language_hint": "italian"
    },
    {
        "query": "A cosa serve il manifest.xml?",
        "expected_answer": "Il file AndroidManifest.xml fornisce informazioni essenziali al sistema sul contenuto dell'app.",
        "language_hint": "italian"
    },
]

for idx, test in enumerate(TEST_CASES, 1):
    query = test["query"]
    expected = test["expected_answer"]
    lang = test.get("language_hint", "italian")
    
    prediction, _ = manager.ask(query, language=lang)
    scores = evaluate_all(prediction, expected, language=lang)
    
    print(f"Test #{idx}")
    print(f"Domanda: {query}")
    print(f"Risposta attesa: {expected}")
    print(f"Risposta modello: {prediction}")
    print("Metriche:")
    for k, v in scores.items():
        print(f"    - {k}: {v:.3f}" if isinstance(v, float) else f"    - {k}: {v}")
    print("-" * 60)

    results.append(scores)

if results:
    print("\nMetriche medie su tutti i test:")
    avg = {k: sum(r[k] for r in results) / len(results) for k in results[0]}
    for k, v in avg.items():
        print(f"  {k}: {v:.3f}")
