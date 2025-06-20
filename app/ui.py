import tkinter as tk
from tkinter import scrolledtext
import threading
import traceback
from QASystemManager import QASystemManager

manager = QASystemManager()

def ask_async(query):
    try:
        risposta, sources = manager.ask(query)

        ground_truth = "Risposta corretta di esempio"
        scores = manager.evaluate(risposta, ground_truth)

        print(f"[🧪 Valutazione]: {query}")
        for metric, score in scores.items():
            print(f"{metric}: {score:.3f}" if isinstance(score, float) else f"{metric}: {score}")

        def update_ui():
            response_text.delete(1.0, tk.END)
            response_text.insert(tk.END, risposta + "\n\n📄 Fonti usate:\n", 'bold')
            for doc in sources:
                response_text.insert(tk.END, "- " + doc.metadata.get("source", "N/A") + "\n")
            btn_ask.config(state=tk.NORMAL)

        root.after(0, update_ui)

    except Exception as e:
        tb_str = traceback.format_exc()
        def show_error():
            response_text.delete(1.0, tk.END)
            response_text.insert(tk.END, f"Errore: {str(e)}\n\n{tb_str}")
            btn_ask.config(state=tk.NORMAL)
        root.after(0, show_error)

def on_ask():
    if not manager.is_ready():
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.END, "Errore: il sistema QA non è stato inizializzato correttamente.\n")
        return

    query = entry.get()
    if not query.strip():
        return

    btn_ask.config(state=tk.DISABLED)
    response_text.delete(1.0, tk.END)
    response_text.insert(tk.END, "Sto elaborando la tua domanda...\n")
    threading.Thread(target=ask_async, args=(query,), daemon=True).start()

# UI setup
root = tk.Tk()
root.title("QA modello Italiano")

tk.Label(root, text="Inserisci la domanda:").pack(padx=10, pady=5)

entry = tk.Entry(root, width=80)
entry.pack(padx=10, pady=5)
entry.focus()

btn_ask = tk.Button(root, text="Chiedi", command=on_ask)
btn_ask.pack(padx=10, pady=5)

response_text = scrolledtext.ScrolledText(root, height=15, width=80)
response_text.tag_config('bold', font=('Helvetica', 10, 'bold'))
response_text.pack(padx=10, pady=5)

root.mainloop()
