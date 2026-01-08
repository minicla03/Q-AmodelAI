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
        "relevant_docs": ["Android.pdf"],
        "summary": "L'utente è uno sviluppatore Junior che sta creando un'app di riproduzione musicale. Ha riscontrato un problema: quando l'utente chiude l'app o spegne lo schermo, la musica si interrompe. Ha provato a usare un semplice Thread Java, ma il sistema operativo uccide il processo per risparmiare memoria. Cerca una soluzione robusta e specifica del framework Android per mantenere l'attività in background."
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
        "relevant_docs": ["Software Design.pdf"],
        "summary": "L'utente sta progettando un sistema per una stazione meteo. Ha un oggetto 'DatiMeteo' che riceve aggiornamenti dai sensori e deve aggiornare automaticamente tre diversi display (temperatura, statistiche e previsioni) senza che l'oggetto 'DatiMeteo' conosca i dettagli specifici di questi display. Vuole disaccoppiare il codice e ha sentito parlare di un pattern comportamentale adatto a questo scopo."
    },
    {
        "query": "Come è strutturata una classe di testing?",
        "expected_answer": (
            "Una classe di testing serve a verificare il funzionamento del codice ed è organizzata in tre parti: "
            "1. Setup, con metodi come setUp() o annotazioni @Before per preparare l'ambiente; "
            "2. Test, dove si usano metodi con assertion per controllare i risultati; "
            "3. Teardown, con metodi come tearDown() o @After per pulire le risorse. "
            "Si possono usare mock per isolare dipendenze e si applica il principio AAA (Arrange-Act-Assert)."
        ),
        "language_hint": "italian",
        "relevant_docs": ["IngSw teo pt2.pdf", "Android.pdf"],
        "summary": "Il team sta adottando la metodologia TDD (Test Driven Development). L'utente ha notato che i suoi test precedenti fallivano in modo casuale perché le variabili non venivano resettate tra un'esecuzione e l'altra. Ha bisogno di capire la struttura standard di una classe JUnit, specificamente come gestire l'inizializzazione e la pulizia delle risorse prima e dopo ogni singolo test."
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
        "relevant_docs": ["Misure Elettroniche.pdf"],
        "summary": "The user is an electrical engineering student working on an analog amplifier project in the lab. They are trying to diagnose a signal distortion issue. They have been using a multimeter but realized it only gives average values and cannot show the fast, transient noise spikes that are causing the audio glitches. They need to understand what specific visualization capabilities this instrument offers."
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
        "relevant_docs": ["Misure Elettroniche.pdf", "Data Analytics.pdf"],
        "summary": "The user is studying for a physics exam on AC circuits. They are confused about why the wall outlet is labeled as 230V when the calculation of the sine wave peak shows it reaches about 325V. They need a conceptual explanation relating AC voltage to the equivalent heat energy produced by a DC source to understand the term 'effective value'."
    },
    {
        "query": "¿Qué es el análisis exploratorio de datos?",
        "expected_answer": (
            "El análisis exploratorio de datos (EDA) es un método para resumir y entender las características principales de un conjunto de datos. "
            "Incluye estadísticas descriptivas como media y desviación estándar, visualizaciones como histogramas y gráficos de dispersión, y la detección de patrones o anomalías. "
            "EDA es importante antes de aplicar modelos complejos para conocer la estructura y calidad de los datos."
        ),
        "language_hint": "spanish",
        "relevant_docs": ["Data Analytics.pdf"],
        "summary": "El usuario es un analista de marketing que acaba de recibir un archivo CSV masivo con datos de comportamiento de clientes. Los datos están sucios, contienen valores nulos y posibles errores. Antes de intentar entrenar un algoritmo de predicción de ventas, quiere saber cuál es la metodología estándar para 'conocer' los datos, visualizar distribuciones y limpiar errores."
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
        "relevant_docs": ["Data Analytics.pdf", "Misure Elettroniche.pdf"],
        "summary": "Un investigador biológico está estudiando el efecto de la temperatura ambiente en la tasa de crecimiento de una planta específica. Ha recopilado datos experimentales y sospecha que existe una relación directa y proporcional. Necesita confirmar si este modelo estadístico es adecuado para predecir el crecimiento futuro basándose en temperaturas no observadas."
    },
    {
        "query": "Welche Arten von Services gibt es in Android?",
        "expected_answer": (
            "In Android gibt es verschiedene Arten von Services: Started Service, Bound Service und Foreground Service. "
            "Started Services werden einmal gestartet und laufen unabhängig, Bound Services erlauben anderen Komponenten die Verbindung, und Foreground Services sind für den Nutzer sichtbar. "
            "Services laufen im Hintergrund und ihr Lebenszyklus wird über Methoden wie onCreate(), onStartCommand(), onBind() und onDestroy() gesteuert."
        ),
        "language_hint": "german",
        "relevant_docs": ["Android.pdf"],
        "summary": "Der Entwickler baut eine Fitness-Tracking-App. Er muss entscheiden, welche Architekturkomponente er verwenden soll: Eine, die einfach Daten im Hintergrund synchronisiert (wie ein Download), oder eine, die aktiv eine Laufstrecke aufzeichnet und dem Benutzer eine Benachrichtigung anzeigt, damit das System den Prozess nicht beendet. Er braucht einen Überblick über die verfügbaren Service-Typen."
    },
    {
        "query": "Wie kommunizieren Activities untereinander?",
        "expected_answer": (
            "Activities kommunizieren über Intents miteinander. "
            "Ein Intent kann Daten enthalten und eine andere Activity starten. "
            "Dies ermöglicht die Navigation zwischen verschiedenen Bildschirmen innerhalb einer App, die im AndroidManifest.xml registriert sein müssen."
        ),
        "language_hint": "german",
        "relevant_docs": ["Android.pdf"],
        "summary": "Der Benutzer erstellt eine E-Commerce-App. Er hat eine Listenansicht (Activity A) mit Produkten und eine Detailansicht (Activity B). Wenn der Nutzer auf ein Produkt klickt, muss Activity B geöffnet werden und wissen, welches Produkt (ID oder Name) angezeigt werden soll. Der Benutzer fragt nach dem Standardmechanismus für diesen Datentransfer und Bildschirmwechsel."
    },
    {
        "query": "Welche Aufgaben hat die AndroidManifest.xml?",
        "expected_answer": (
            "Die AndroidManifest.xml definiert alle Komponenten einer App, wie Activities, Services und Berechtigungen. "
            "Sie legt die Haupt-Activity fest, beschreibt Intent-Filter und ist notwendig, damit das Betriebssystem die App korrekt ausführt. "
            "Ohne Manifest können die Komponenten nicht erkannt werden."
        ),
        "language_hint": "german",
        "relevant_docs": ["Android.pdf"],
        "summary": "Ein Anfänger in der Android-Entwicklung hat eine neue Activity-Klasse im Java-Code erstellt, aber jedes Mal, wenn er versucht, sie zu starten, stürzt die App mit einer 'ActivityNotFoundException' ab. Wir haben bereits den Java-Code geprüft und er scheint korrekt zu sein. Der Verdacht liegt auf einer fehlenden Registrierung in den Konfigurationsdateien."
    },
    {
        "query": "Was versteht man unter Software-Design-Patterns?",
        "expected_answer": (
            "Software-Design-Patterns sind bewährte Lösungen für häufig auftretende Probleme in der Softwareentwicklung. "
            "Sie bieten wiederverwendbare Konzepte, die die Wartbarkeit und Flexibilität erhöhen. "
            "Ein Beispiel ist das Observer-Muster, bei dem Objekte automatisch benachrichtigt werden, wenn sich der Zustand eines anderen Objekts ändert."
        ),
        "language_hint": "german",
        "relevant_docs": ["Software Design.pdf"],
        "summary": "In einem Code-Review wurde dem Benutzer gesagt, sein Code sei schwer zu warten und er solle 'gängige Patterns' verwenden. Der Benutzer fühlt sich überfordert und möchte verstehen, ob Design Patterns fertige Code-Bibliotheken sind oder eher abstrakte Lösungskonzepte für architektonische Probleme, um die Kommunikation im Team zu verbessern."
    },
    {
        "query": "Welche Schritte umfasst eine typische Testklasse?",
        "expected_answer": (
            "Eine Testklasse umfasst typischerweise drei Schritte: "
            "Setup zur Vorbereitung der Umgebung, Testmethoden mit Assertions zur Überprüfung des Codes, und Teardown zur Freigabe von Ressourcen. "
            "Mocks können zur Isolation von Abhängigkeiten genutzt werden, und das AAA-Prinzip (Arrange-Act-Assert) wird angewendet."
        ),
        "language_hint": "german",
        "relevant_docs": ["IngSw teo pt2.pdf", "Android.pdf"],
        "summary": "Der Benutzer schreibt Unit-Tests für eine Datenbankverbindung. Er hat das Problem, dass er vor jedem Test eine saubere Verbindung herstellen und sie danach schließen muss, um Seiteneffekte zu vermeiden. Er sucht nach der formalen Struktur (Setup/Teardown) und den Best Practices, um Tests unabhängig voneinander und wiederholbar zu machen."
    },
    {
        "query": "Was kann ein Oszilloskop messen?",
        "expected_answer": (
            "Ein Oszilloskop kann Spannungen über die Zeit darstellen, Signalformen analysieren und Frequenz sowie Amplitude messen. "
            "Es ermöglicht das Triggern auf bestimmte Signalereignisse und ist ein unverzichtbares Werkzeug beim Testen und Debuggen elektronischer Schaltungen."
        ),
        "language_hint": "german",
        "relevant_docs": ["Misure Elettroniche.pdf"],
        "summary": "Ein Tontechniker überprüft einen Vorverstärker auf Fehler. Er muss nicht nur wissen, ob Strom fließt, sondern will die Wellenform sehen, um zu prüfen, ob das Signal 'abgeschnitten' (Clipping) wird oder ob unerwünschtes Rauschen auf der Frequenz liegt. Er fragt nach den spezifischen Messmöglichkeiten dieses Geräts im Vergleich zu einfachen Messgeräten."
    },
    {
        "query": "Welche Technologien werden bei Big Data eingesetzt?",
        "expected_answer": (
            "Für Big Data werden Technologien wie Hadoop und Spark eingesetzt, um sehr große und vielfältige Datensätze zu speichern und zu verarbeiten. "
            "Ziele sind Analyse, Prognose und Personalisierung, während Herausforderungen Speicher, Geschwindigkeit und Sicherheit betreffen."
        ),
        "language_hint": "german",
        "relevant_docs": ["Data Analytics.pdf"],
        "summary": "Ein IT-Architekt bei einem großen Einzelhändler plant die Migration von traditionellen SQL-Datenbanken zu einer modernen Data-Lake-Infrastruktur. Das Unternehmen sammelt jetzt Petabytes an unstrukturierten Daten (Logs, Bilder, Klicks). Der Benutzer benötigt einen Überblick über die aktuellen Frameworks für verteiltes Speichern und Verarbeiten (wie MapReduce-Konzepte), um eine Entscheidungsgrundlage für das Management zu erstellen."
    },
]