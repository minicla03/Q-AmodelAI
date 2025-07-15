import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import threading
import traceback
from QASystemManager import QASystemManager
from qa_utils import detect_language_from_query

manager = QASystemManager()

def ask_async(query, default_language):
    language = detect_language_from_query(query) or default_language
    try:
        risposta, sources = manager.ask(query, language)

        def update_ui():
            response_text.config(state=tk.NORMAL)
            response_text.delete(1.0, tk.END)
            if isinstance(risposta, dict):
                response_text.insert(tk.END, risposta.get("output_text", "") + "\n\nFonti usate:\n", 'bold')
                for doc in sources:
                    response_text.insert(tk.END, "- " + doc.metadata.get("source", "N/A") + "\n")
            else:
                response_text.insert(tk.END, str(risposta) + "\n", 'bold')
            response_text.config(state=tk.DISABLED)
            btn_ask.config(state=tk.NORMAL)

        root.after(0, update_ui)

    except Exception as e:
        tb_str = traceback.format_exc()
        def show_error(e=e, tb_str=tb_str): 
            response_text.config(state=tk.NORMAL)
            response_text.delete(1.0, tk.END)
            response_text.insert(tk.END, f"Errore: {str(e)}\n\n{tb_str}")
            response_text.config(state=tk.DISABLED)
            btn_ask.config(state=tk.NORMAL)
        root.after(0, show_error)

def on_ask():
    if not manager.is_ready():
        response_text.config(state=tk.NORMAL)
        response_text.delete(1.0, tk.END)
        response_text.insert(tk.END, "Errore: il sistema QA non è stato inizializzato correttamente.\n")
        response_text.config(state=tk.DISABLED)
        return

    query = entry.get()
    if not query.strip():
        return

    btn_ask.config(state=tk.DISABLED)
    response_text.config(state=tk.NORMAL)
    response_text.delete(1.0, tk.END)
    response_text.insert(tk.END, "Sto elaborando la tua domanda...\n")
    response_text.config(state=tk.DISABLED)
    default_language = "italiano" 
    threading.Thread(target=ask_async, args=(query, default_language), daemon=True).start()


def on_upload_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        try:
            print(f"[DEBUG] Aggiunta documento: {file_path}")
            manager.add_document(file_path)
            msg = f"\nDocumento aggiunto: {file_path}\n"
        except Exception as e:
            print(f"[ERROR] Errore durante l'aggiunta del documento: {e}")
            msg = f"\nErrore caricamento: {e}\n"
        response_text.config(state=tk.NORMAL)
        response_text.insert(tk.END, msg)
        response_text.config(state=tk.DISABLED)

def on_show_documents():
    try:
        docs = manager.list_documents()
        if not docs:
            msg = "\nNessun documento caricato.\n"
        else:
            msg = "\nDocumenti attualmente caricati:\n"
            for i, doc in enumerate(docs, 1):
                msg += f"{i}. {doc}\n"
    except Exception as e:
        msg = f"\nErrore nella lettura dei documenti: {e}\n"

    response_text.config(state=tk.NORMAL)
    response_text.delete(1.0, tk.END)
    response_text.insert(tk.END, msg)
    response_text.config(state=tk.DISABLED)

def on_delete_pdf():
    try:
        docs = manager.list_documents()
        if not docs:
            msg = "\nNessun documento da eliminare.\n"
            response_text.config(state=tk.NORMAL)
            response_text.insert(tk.END, msg)
            response_text.config(state=tk.DISABLED)
            return

        doc_list_str = "\n".join([f"{i+1}. {doc}" for i, doc in enumerate(docs)])
        choice_input = simpledialog.askstring(
            "Elimina Documento",
            f"Quale documento vuoi eliminare?\n\nPuoi inserire il nome o il numero corrispondente:\n\n{doc_list_str}"
        )

        msg = ""
        selected_doc_name = None

        if choice_input:
            choice_input = choice_input.strip()

            if choice_input.isdigit():
                index = int(choice_input) - 1
                if 0 <= index < len(docs):
                    selected_doc_name = docs[index]
                else:
                    msg = "\nNumero fuori intervallo.\n"
            else:
                if choice_input in docs:
                    selected_doc_name = choice_input
                else:
                    matching_docs = [doc for doc in docs if choice_input.lower() in doc.lower()]
                    if len(matching_docs) == 1:
                        selected_doc_name = matching_docs[0]
                    elif len(matching_docs) > 1:
                        msg = f"\nPiù documenti corrispondono a '{choice_input}'. Sii più specifico.\n"
                    else:
                        msg = f"\nDocumento '{choice_input}' non trovato.\n"

            if selected_doc_name:
                confirmed = messagebox.askyesno(
                    "Conferma Eliminazione",
                    f"Sei sicuro di voler eliminare '{selected_doc_name}'?\nQuesta operazione è irreversibile."
                )
                if confirmed:
                    success = manager.delete_document(selected_doc_name)
                    if success:
                        msg = f"\nDocumento '{selected_doc_name}' eliminato con successo.\n"
                    else:
                        msg = f"\nErrore durante l'eliminazione di '{selected_doc_name}'. Controlla i log.\n"
                else:
                    msg = "\nOperazione di eliminazione annullata.\n"
        else:
            msg = "\nNessun documento selezionato per l'eliminazione.\n"

    except Exception as e:
        msg = f"\nErrore durante l'operazione di eliminazione: {e}\n"
        traceback.print_exc()

    response_text.config(state=tk.NORMAL)
    response_text.insert(tk.END, msg)
    response_text.config(state=tk.DISABLED)

# UI setup
root = tk.Tk()
root.title("QA model for notes")
root.geometry("700x450")
root.configure(bg="#f0f4f8")

# Font settings
font_label = ("Segoe UI", 11)
font_entry = ("Segoe UI", 11)
font_button = ("Segoe UI", 11, "bold")
font_text = ("Consolas", 11)

# Container frame
frame = tk.Frame(root, bg="#f0f4f8", padx=20, pady=20)
frame.pack(expand=True, fill=tk.BOTH)

label = tk.Label(frame, text="Inserisci la domanda:", font=font_label, bg="#f0f4f8", fg="#333")
label.pack(anchor="w", pady=(0, 8))

entry = tk.Entry(frame, font=font_entry, width=60, relief=tk.FLAT, bd=2)
entry.pack(fill=tk.X, pady=(0, 12))
entry.focus()

button_frame = tk.Frame(frame, bg="#f0f4f8")
button_frame.pack(pady=(0, 15), anchor="center")

#bottone per fare la richiesta
btn_ask = tk.Button(button_frame, text="Chiedi", font=font_button, bg="#4a90e2", fg="white", activebackground="#357ABD",
                    activeforeground="white", command=on_ask, cursor="hand2")
btn_ask.pack(side=tk.LEFT, padx=(0, 10))

# bottone per caricare i doc
btn_upload = tk.Button(button_frame, text="Carica PDF", font=font_button, bg="#27ae60", fg="white",
                       activebackground="#1e8449", command=on_upload_pdf)
btn_upload.pack(side=tk.LEFT)

#bottone per mostrare i doc
btn_show_docs = tk.Button(button_frame, text="Mostra documenti", font=font_button, bg="#f39c12", fg="white",
                          activebackground="#d68910", command=on_show_documents)
btn_show_docs.pack(side=tk.LEFT, padx=(10, 0))

#bottone pe cancellare
btn_delete_pdf = tk.Button(button_frame, text="Elimina PDF", font=font_button, bg="#e74c3c", fg="white",
                            activebackground="#c0392b", command=on_delete_pdf)
btn_delete_pdf.pack(side=tk.LEFT, padx=(10, 0))

response_text = scrolledtext.ScrolledText(frame, font=font_text, height=15, wrap=tk.WORD, relief=tk.FLAT, bd=2)
response_text.tag_config('bold', font=("Segoe UI", 11, "bold"))
response_text.config(state=tk.DISABLED)
response_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()
