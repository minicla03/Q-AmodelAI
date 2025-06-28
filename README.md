# Q-AmodelAI

Sistema di domanda e risposta (QA) multilingue basato su documenti PDF caricati dall'utente, con interfaccia grafica tramite Tkinter.

---

## 💡 Descrizione

Questa applicazione consente di:

- Caricare PDF personali tramite un'interfaccia GUI;
- Eseguire domande sui contenuti caricati, con supporto multilingua (IT, EN, ES, FR, DE);
- Visualizzare fonti e documenti usati nella risposta;
- Valutare automaticamente le risposte tramite uno script di testing con metriche NLP.

---

## ⚙️ Requisiti

- Python 3.10+
- [Ollama](https://ollama.com/) installato e attivo con modello `llama3:latest`

---

## 📦 Installazione

```bash
# Clona il repository
git clone https://github.com/minicla03/Q-AmodelAI.git
cd Q-AmodelAI

# (Opzionale) Crea un ambiente virtuale
python -m venv venv
source venv/bin/activate      # Su Windows: venv\Scripts\activate

# Installa le dipendenze
pip install -r requirements.txt

# Avvia Ollama (in un terminale separato)
ollama run llama3
```

---

## 🚀 Avvio dell'interfaccia grafica

```bash
python ui.py
```

---

## 📂 Struttura cartelle

- `data/`: PDF caricati dall’utente
- `chroma_db/`: archivio vettoriale persistente (ChromaDB)
- `app/`: script per la gestione dell'app

---

## 🔍 Componenti principali della cartella app/

| File/Modulo            | Funzione                                                          |
|------------------------|-------------------------------------------------------------------|
| `ui.py`                | Interfaccia GUI (domanda, upload, mostra documenti)              |
| `QASystemManager.py`   | Gestione vectorstore e logica di sistema                         |
| `ingestion.py`         | Parsing PDF, chunking e persistenza con Chroma                   |
| `retrival.py`          | Recupero documenti e costruzione risposte                        |
| `evaluation_script.py` | Testing automatico delle risposte (metriche NLP)                 |
| `qa_utils.py`          | Utility di pulizia, rilevamento lingua, ecc.                     |

---

## 📊 Valutazione del sistema QA

Per testare il sistema su un insieme di domande con risposte attese:

```bash
python evaluation_script.py
```

Salverà un file `metriche_medie.txt` con le metriche F1, BLEU, ROUGE-L, Similarità semantica, Precision/Recall contestuali.

---

## 🗃️ Gestione documenti

- ✅ Carica PDF: tramite GUI
- ✅ Mostra documenti: pulsante dedicato
- 🔜 Cancellazione documenti: da implementare in futuro

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

1. Carica uno o più PDF (es. appunti universitari)
2. Inserisci una domanda nella GUI, ad es.:
   - `Spiega il pattern Observer in italiano`
   - `What is an oscilloscope?`
3. Ottieni una risposta sintetica, chiara, con fonti utilizzate
