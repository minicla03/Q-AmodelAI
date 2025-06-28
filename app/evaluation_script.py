from QASystemManager import QASystemManager
from evaluation import evaluate_all, compute_context_precision_recall

manager = QASystemManager()

if not manager.is_ready():
    print("QA System non pronto.")
    exit()

print("Inizio valutazione su test set...\n")

results = []

TEST_CASES = [
    {
        "query": "Cosa sono i servizi in Android?",
        "expected_answer": (
            "I servizi in Android sono componenti che eseguono operazioni in background senza mostrare un'interfaccia. "
            "Possono continuare a funzionare anche se l'app non è visibile. "
            "Ci sono tipi diversi come Started Service (avviato da un componente), Bound Service (permette a componenti di connettersi) e Foreground Service (che l'utente nota). "
            "Hanno un ciclo di vita gestito da metodi come onCreate(), onStartCommand(), onBind() e onDestroy()."
        ),
        "language_hint": "italian",
        "relevant_docs": ["Android.pdf"]
    },
    {
        "query": "Cos'è un'activity?",
        "expected_answer": (
            "Un'activity in Android è una schermata con cui l'utente interagisce. "
            "È una classe che gestisce il ciclo di vita con metodi come onCreate(), onStart(), onResume(), onPause(), onStop() e onDestroy(). "
            "Le activity comunicano tramite Intent e si dichiarano nel file AndroidManifest.xml. "
            "Un'app può avere più activity con scopi diversi."
        ),
        "language_hint": "italian",
        "relevant_docs": ["Android.pdf"]
    },
    {
        "query": "A cosa serve il manifest.xml?",
        "expected_answer": (
            "Il file AndroidManifest.xml è essenziale per configurare un'app Android. "
            "Contiene informazioni su tutti i componenti come activity, servizi, e permessi richiesti. "
            "Definisce quale activity è quella principale e può specificare filtri per gli intent. "
            "Si trova nella cartella principale del progetto."
        ),
        "language_hint": "italian",
        "relevant_docs": ["Android.pdf"]
    },
    {
        "query": "Cos'è il modello a cascata in ingegneria del software?",
        "expected_answer": (
            "Il modello a cascata è un metodo di sviluppo software in cui le fasi seguono un ordine preciso e lineare: "
            "analisi dei requisiti, progettazione, implementazione, test, rilascio e manutenzione. "
            "Ogni fase si completa prima di iniziare la successiva, senza tornare indietro. "
            "È semplice da gestire ma poco flessibile ai cambiamenti."
        ),
        "language_hint": "italian",
        "relevant_docs": ["IngSw teo pt2.pdf"]
    },
    {
        "query": "Cos'è il pattern Observer in ingegneria del software?",
        "expected_answer": (
            "Il pattern Observer è un modello che definisce una relazione uno-a-molti tra oggetti. "
            "Quando un oggetto cambia stato, tutti gli oggetti osservatori vengono aggiornati automaticamente. "
            "Prevede un'interfaccia Observer con un metodo update() e un Subject che gestisce la lista degli osservatori. "
            "È utile per sistemi reattivi e notifiche."
        ),
        "language_hint": "italian",
        "relevant_docs": ["Software Design.pdf"]
    },
    {
        "query": "Come è strutturata una classe di testing?",
        "expected_answer": (
            "Una classe di testing serve a verificare il funzionamento del codice ed è organizzata in tre parti: "
            "1. Setup, con metodi come setUp() o annotazioni @Before per preparare l'ambiente; "
            "2. Test, dove si usano metodi con assertion per controllare i risultati; "
            "3. Teardown, con metodi come tearDown() o @After per pulire le risorse. "
            "Si possono usare mock per isolare dipendenze e si applica il principio AAA (Arrange-Act-Assert). "
            "Framework comuni sono JUnit, pytest e Espresso."
        ),
        "language_hint": "italian",
        "relevant_docs": ["IngSw teo pt2.pdf", "Android.pdf"]
    },
    {
        "query": "What is the purpose of an oscilloscope?",
        "expected_answer": (
            "An oscilloscope is an electronic instrument that shows how voltage signals change over time. "
            "It helps engineers see signal features like frequency, amplitude, and shape. "
            "Modern oscilloscopes capture analog and digital signals and offer tools like triggering and measurements. "
            "They are essential for debugging and testing electronic circuits."
        ),
        "language_hint": "english",
        "relevant_docs": ["Misure Elettroniche.pdf"]
    },
    {
        "query": "Explain the concept of RMS voltage.",
        "expected_answer": (
            "RMS voltage (Root Mean Square) is a way to express the effective value of an AC voltage. "
            "It is calculated by taking the square root of the average of the squared instantaneous voltages over one cycle. "
            "For a sine wave, RMS equals the peak voltage divided by √2 (about 0.707 times the peak). "
            "RMS values relate AC voltage to the equivalent DC power and are the standard for measurements."
        ),
        "language_hint": "english",
        "relevant_docs": ["Misure Elettroniche.pdf", "Data Analytics.pdf"]
    },
    {
        "query": "¿Qué es el análisis exploratorio de datos?",
        "expected_answer": (
            "El análisis exploratorio de datos (EDA) es un método para resumir y entender las características principales de un conjunto de datos. "
            "Incluye estadísticas descriptivas como media y desviación estándar, visualizaciones como histogramas y gráficos de dispersión, y la detección de patrones o anomalías. "
            "EDA es importante antes de aplicar modelos complejos para conocer la estructura y calidad de los datos."
        ),
        "language_hint": "spanish",
        "relevant_docs": ["Data Analytics.pdf"]
    },
    {
        "query": "¿Para qué sirve la regresión lineal?",
        "expected_answer": (
            "La regresión lineal es una técnica para modelar la relación entre una variable dependiente y una o más variables independientes. "
            "Permite predecir valores y medir la fuerza de esa relación. "
            "Hay regresión simple (una variable) y múltiple (varias variables). "
            "Se usa en economía, ciencias sociales y machine learning, bajo supuestos como linealidad y normalidad de errores."
        ),
        "language_hint": "spanish",
        "relevant_docs": ["Data Analytics.pdf", "Misure Elettroniche.pdf"]
    },
    {
        "query": "Qu'est-ce que le big data?",
        "expected_answer": (
            "Le big data désigne de très grands ensembles de données caractérisés par cinq aspects : volume, vélocité, variété, véracité et valeur. "
            "Ces données dépassent les capacités des outils traditionnels et nécessitent des technologies spécifiques comme Hadoop ou Spark. "
            "Le big data est utilisé pour l’analyse prédictive, la personnalisation et d’autres domaines, avec des défis liés au stockage et à la sécurité."
        ),
        "language_hint": "french",
        "relevant_docs": ["Data Analytics.pdf"]
    },
    {
        "query": "À quoi sert une analyse prédictive?",
        "expected_answer": (
            "L’analyse prédictive utilise des données historiques et des algorithmes pour prévoir des événements futurs. "
            "Elle emploie des méthodes comme la régression et les arbres de décision. "
            "Ses applications incluent la prévision de la demande, la détection de fraudes et le marketing ciblé. "
            "Le processus comprend la collecte, la préparation des données, l’entraînement des modèles et la validation."
        ),
        "language_hint": "french",
        "relevant_docs": ["DataAnalytics.pdf"]
    },
]


for idx, test in enumerate(TEST_CASES, 1):
    query = test["query"]
    expected = test["expected_answer"]
    lang = test.get("language_hint", "italian")
    relevant_docs = test.get("relevant_docs", [])

    prediction, source_docs = manager.ask(query, language=lang)
    print(type(prediction), type(source_docs)) 
    output_text = prediction.get("output_text", "")

    retrieved_sources = [doc.metadata.get("source") for doc in source_docs if doc.metadata.get("source")]

    qa_scores = evaluate_all(output_text, expected, language=lang)
    context_precision, context_recall = compute_context_precision_recall(retrieved_sources, relevant_docs)

    print(f"Test #{idx}")
    print(f"Domanda: {query}")
    print(f"Risposta attesa: {expected}")
    print(f"Risposta modello: {output_text}")
    print("Metriche:")
    for key, value in qa_scores.items():
        print(f"    - {key}: {value:.3f}" if isinstance(value, float) else f"    - {key}: {value}")
    print(f"    - Context Precision: {context_precision:.3f}")
    print(f"    - Context Recall: {context_recall:.3f}")
    print("-" * 60)

    qa_scores["Context Precision"] = context_precision
    qa_scores["Context Recall"] = context_recall
    results.append(qa_scores)

if results:
    print("\nMetriche medie su tutti i test:")
    avg = {key: sum(r[key] for r in results) / len(results) for key in results[0]}
    
    for key, valuea in avg.items():
        print(f"  {key}: {value:.3f}")

    with open("metriche_medie.txt", "w", encoding="utf-8") as f:
        f.write(f"Metriche medie su tutti i test:\n\n")
        for key, value in avg.items():
            f.write(f"{key}: {value:.3f}\n")

