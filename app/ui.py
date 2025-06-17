import tkinter as tk
from tkinter import scrolledtext
import threading
from script import setup_qa_system, ask_question

qa_chain = setup_qa_system()

def ask_async(query):
    try:
        risposta, sources = ask_question(qa_chain, query)
        def update_ui():
            response_text.delete(1.0, tk.END)
            response_text.insert(tk.END, risposta + "\n\n📄 Fonti usate:\n")
            for doc in sources:
                response_text.insert(tk.END, "- " + doc.metadata.get("source", "N/A") + "\n")
            btn_ask.config(state=tk.NORMAL)
        root.after(0, update_ui)
    except Exception as e:
        def show_error():
            response_text.delete(1.0, tk.END)
            response_text.insert(tk.END, f"Errore: {str(e)}")
            btn_ask.config(state=tk.NORMAL)
        root.after(0, show_error)

def on_ask():
    query = entry.get()
    if not query.strip():
        return
    btn_ask.config(state=tk.DISABLED)
    response_text.delete(1.0, tk.END)
    response_text.insert(tk.END, "Sto elaborando la tua domanda...\n")
    threading.Thread(target=ask_async, args=(query,), daemon=True).start()

root = tk.Tk()
root.title("QA modello Italiano")

tk.Label(root, text="Inserisci la domanda:").pack(padx=10, pady=5)

entry = tk.Entry(root, width=80)
entry.pack(padx=10, pady=5)
entry.focus()

btn_ask = tk.Button(root, text="Chiedi", command=on_ask)
btn_ask.pack(padx=10, pady=5)

response_text = scrolledtext.ScrolledText(root, height=15, width=80)
response_text.pack(padx=10, pady=5)

root.mainloop()
