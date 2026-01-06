<p align="center">
  <img src="https://github.com/user-attachments/assets/16191aa5-d343-45f7-8910-8867d5eb4661" alt="Cognix Icon" width="250">
</p>

# 🤖🧠 Cognix

Sistema di domanda e risposta (QA) multilingue basato su documenti PDF caricati dall'utente

## ⚠️ In sviluppo

Questo progetto è attivamente in sviluppo 🛠️.  
Nuove funzionalità in arrivo…  

<img width="580" height="450" alt="image" src="https://github.com/user-attachments/assets/cde871c9-4982-4e44-b24a-149ee9456447" />

---

## 💡 Descrizione

Questa applicazione consente di:

- Caricare PDF personali tramite un'interfaccia GUI;
- Eseguire domande sui contenuti caricati, con supporto multilingua (IT, EN, ES, FR, DE);
- Visualizzare fonti e documenti usati nella risposta;
- Possibilità di creare FlashCard e Quiz
---

## ⚙️ Requisiti

- Python 3.10+
- [LLM](https://ollama.com/) installato e attivo con modello `llama3:latest`
- [Ollama](https://ollama.com/) installato e attivo con modello `llama3:latest`

---

## 📦 Installazione

### Prerequisiti

1. **Python 3.10+** installato sul sistema
2. **Ollama** installato e in esecuzione con il modello `llama3:latest`
   ```bash
   # Installa Ollama da https://ollama.com/
   ollama pull llama3:latest
   ollama serve
   ```
3. **MongoDB** installato e in esecuzione (locale o remoto)
4. **Redis** installato e in esecuzione (locale o remoto)

### Setup

1. **Clona il repository**
   ```bash
   git clone https://github.com/minicla03/Cognix.git
   cd Cognix
   ```

2. **Crea un ambiente virtuale Python**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt  # Se presente
   # Oppure installa manualmente le dipendenze principali:
   pip install streamlit langchain langchain-community langchain-huggingface
   pip install pymongo redis chromadb sentence-transformers
   pip install python-dotenv langchain-chroma langchain-cohere
   ```

4. **Configura le variabili d'ambiente**
   
   Crea un file `.env` nella root del progetto:
   ```env
   # MongoDB
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=rag_system
   
   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   # REDIS_PASSWORD=your_password  # Se necessario
   
   # Cohere (per reranking, opzionale)
   # COHERE_API_KEY=your_api_key
   ```

5. **Avvia l'applicazione**
   ```bash
   cd presentation
   streamlit run notebook_page.py
   ```

L'applicazione sarà disponibile su `http://localhost:8501`

---

## 📂 Struttura cartelle


```
Cognix/
├── presentation/           # Frontend Streamlit
│   ├── notebook_page.py   # Pagina principale per gestione notebook
│   └── pages/
│       └── chat.py        # Interfaccia chat per interazione QA
│
├── rag_logic/             # Logica RAG e AI
│   ├── agents/            # Agenti AI
│   │   ├── routing_agent.py    # Router per selezione strumento
│   │   └── summarizer_agent.py # Agente per riassunti
│   ├── tools/             # Strumenti specializzati
│   │   ├── QATool.py      # Strumento Q&A
│   │   ├── FlashcardTool.py # Generazione flashcard
│   │   └── QuizTool.py    # Generazione quiz
│   ├── ingestion/         # Ingestion documenti
│   │   ├── ingestion.py   # Pipeline di ingestione
│   │   └── DocumentLoaderStrategy.py # Strategy pattern per loader
│   ├── memory/            # Gestori memoria
│   │   ├── NotebookManager.py  # Gestione notebook
│   │   ├── ChatManager.py      # Gestione chat
│   │   ├── DocumentManager.py  # Gestione documenti
│   │   ├── FlashcardManager.py # Gestione flashcard
│   │   └── QuizManager.py      # Gestione quiz
│   └── llm/               # Interfaccia LLM
│       └── LLM.py         # Wrapper per Ollama
│
├── persistence/           # Layer persistenza dati
│   ├── long_term_memory/  # Memoria persistente (MongoDB)
│   │   └── mongo/
│   │       └── MongoDBMS.py
│   ├── short_term_memory/ # Cache (Redis)
│   │   └── redis/
│   │       └── RedisDBMS.py
│   └── model/             # Modelli dati
│
├── evaluation/            # Script di valutazione
│   ├── tool_selection_eval/    # Test routing agent
│   ├── tool_eval/              # Test strumenti (QA, etc.)
│   └── summary_generation/     # Test summarizer
│
└── test/                  # Test unitari
    └── unit/
```

---

## 🔍 Componenti principali

### 🤖 Agenti AI

- **Routing Agent**: Analizza la query dell'utente e decide quale strumento utilizzare (QA, Flashcard, Quiz)
- **Summarizer Agent**: Genera riassunti contestuali dei documenti per migliorare la qualità delle risposte

### 🛠️ Strumenti (Tools)

1. **QA Tool**: Risponde a domande basandosi sul contesto recuperato dai documenti caricati
2. **Flashcard Tool**: Genera carte di studio da documenti
3. **Quiz Tool**: Crea quiz interattivi basati sul contenuto

### 📚 Sistema di Ingestion

- Supporta caricamento documenti PDF
- Splitting intelligente del testo con chunk overlap
- Embedding multilingue usando `paraphrase-multilingual-MiniLM-L12-v2`
- Vector store basato su **ChromaDB** per ricerca semantica
- Retrieval con reranking opzionale (Cohere)

### 💾 Persistenza

- **MongoDB**: Storage long-term per notebook, documenti, flashcard e quiz
- **Redis**: Cache per sessioni chat attive e stato temporaneo
- **ChromaDB**: Database vettoriale per embedding e ricerca semantica

---

## 📊 Valutazione del sistema QA

Il progetto include una suite completa di valutazione per garantire qualità e accuratezza:

### Test del Router Agent
- Valuta la capacità di selezione dello strumento corretto
- Test cases multilingua per verificare il routing appropriato
- Report generato in `evaluation/tool_selection_eval/router_test_report.html`

### Test del QA Tool
- Verifica accuratezza delle risposte generate
- Valutazione della rilevanza dei documenti recuperati
- Metriche di performance e qualità

### Test del Summarizer
- Controllo qualità dei riassunti generati
- Verifica della conservazione delle informazioni chiave

Per eseguire le valutazioni:
```bash
cd evaluation
python script.py
```

---

## 🗃️ Gestione documenti

### Caricamento

1. Crea o seleziona un notebook dalla pagina principale
2. Carica uno o più file PDF tramite l'interfaccia
3. I documenti vengono processati automaticamente:
   - Estrazione del testo
   - Chunking con overlap
   - Generazione embedding
   - Storage in ChromaDB

### Organizzazione

- **Notebook**: Contenitori logici per raggruppare documenti correlati
- Ogni notebook ha il proprio vector store isolato
- Supporto per multipli documenti per notebook

### Retrieval

- Ricerca semantica basata su similarity
- Reranking opzionale per migliorare la rilevanza
- Context window ottimizzato per LLM

---

## 🌐 Supporto multilingua

Lingue supportate (rilevamento automatico o esplicitazione nella query):

- Italiano
- Inglese
- Spagnolo
- Francese
- Tedesco

---

## 🧪 Esempio d’uso

### Scenario 1: Domanda e Risposta

1. **Avvia l'applicazione**
   ```bash
   cd presentation
   streamlit run notebook_page.py
   ```

2. **Crea un nuovo notebook**
   - Inserisci un nome (es. "Appunti Ingegneria")
   - Clicca su "Crea"

3. **Carica documenti PDF**
   - Seleziona il notebook appena creato
   - Carica uno o più PDF (es. appunti universitari, manuali)
   - Attendi il completamento dell'ingestion

4. **Inizia a fare domande**
   - Vai alla pagina Chat
   - Inserisci domande come:
     - `Spiega il pattern Observer in italiano`
     - `What is an oscilloscope?`
     - `¿Qué es la inteligencia artificial?`
   
5. **Ricevi risposte contestuali**
   - Risposta sintetica e chiara
   - Fonti documentali utilizzate
   - Supporto multilingua automatico

### Scenario 2: Generazione Flashcard 

```
Query: "Genera flashcard sul design pattern Strategy"
→ Sistema crea carte studio con domanda/risposta
```

### Scenario 3: Creazione Quiz 

```
Query: "Crea un quiz sulle basi di elettronica"
→ Sistema genera domande a scelta multipla
```

---

## 🏗️ Architettura

### Flusso RAG (Retrieval-Augmented Generation)

```
User Query → Routing Agent → Tool Selection
                ↓
           [QA Tool / Flashcard Tool / Quiz Tool]
                ↓
    Document Retrieval (ChromaDB) → Reranking (optional)
                ↓
    Context + Prompt → LLM
                ↓
            Response + Sources
```

### Pattern e Design

- **Strategy Pattern**: Per gestione loader documenti e tools
- **Singleton Pattern**: Per connessioni database (MongoDB, Redis)
- **Manager Pattern**: Per orchestrazione memoria e sessioni
- **Agent Pattern**: Per routing intelligente e summarization

---

## ⚡ Features

✅ **Implementate**
- Upload e processing PDF multilingua
- Q&A basato su RAG con retrieval semantico
- Routing intelligente query → strumento
- Gestione notebook e sessioni chat
- Supporto 5 lingue (IT, EN, ES, FR, DE)
- Vector store con ChromaDB
- Persistenza dati (MongoDB + Redis)
- Suite di valutazione qualità
- CLI per prova
- semplice interfaccia usando Streamilit

🚧 **In sviluppo**
- Miglioramento UI/UX
- Export risposte in vari formati

---

## 🔧 Troubleshooting

### Ollama non risponde
```bash
# Verifica che Ollama sia in esecuzione
ollama serve

# Verifica che il modello sia scaricato
ollama list
ollama pull llama3:latest
```

### Errore connessione MongoDB
```bash
# Verifica che MongoDB sia in esecuzione
mongosh --eval "db.adminCommand('ping')"

# Oppure avvia MongoDB
mongod --dbpath /path/to/your/data
```

### Errore connessione Redis
```bash
# Verifica che Redis sia in esecuzione
redis-cli ping

# Oppure avvia Redis
redis-server
```

### Problemi con embeddings
```bash
# Assicurati che i modelli Hugging Face siano scaricati
# Al primo avvio potrebbero essere necessari alcuni minuti
# per il download automatico dei modelli
```

---

## 🤝 Contribuire

Contributi, issues e feature requests sono benvenuti!

1. Fork il progetto
2. Crea un branch per la tua feature (`git checkout -b feature/newFeature`)
3. Commit le modifiche (`git commit -m 'Add some newFeature'`)
4. Push al branch (`git push origin feature/newFeature`)
5. Apri una Pull Request

---

## 👨‍💻 Autore

**minicla03**

- GitHub: [@minicla03](https://github.com/minicla03)
