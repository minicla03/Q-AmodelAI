import logging

from rag_logic.llm.LLM import LLM


def main():
    logging.basicConfig(level=logging.INFO)

    # Istanza singleton
    ollama = LLM()

    # Prompt di test
    prompt = "Spiegami in una frase cosa è un automa a stati finiti."

    print("\n=== TEST INVOCATION ===")
    try:
        response = ollama.invoke(prompt, config=None, toon_format=False)
        print("Risposta del modello:")
        print(response)
    except Exception as e:
        print("Errore durante l'invocazione:")
        print(e)


if __name__ == "__main__":
    main()
