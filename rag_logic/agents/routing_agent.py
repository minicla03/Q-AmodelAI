import logging
import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from rag_logic.llm.LLM import LLM

logger = logging.getLogger(__name__)

def router_agent(user_query, toon_format, language_hint="italian"):

    logger.info("Avvio router_agent per query: %s", user_query)

    template = """
        You are an intelligent task router for a Retrieval-Augmented Generation (RAG) system.
        Your job is to analyze the user's request and decide which function should be executed.
        
        Available functions:
        1. QA_TOOL → Answers a question based on the context retrieved from documents.
        2. FLASHCARD_TOOL → Generates study flashcards (question/answer pairs) from the content.
        3. QUIZ_TOOL → Generates quiz from the content.
        
        Guidelines:
        - Use the language of the user's query if detectable, otherwise fallback to {language_hint}.
        - If the query asks for explanations, summaries, or answers → QA_TOOL.
        - If the query asks to generate flashcards → FLASHCARD_TOOL.
        - If the query asks to generate quiz questions → QUIZ_TOOL.
        - If multiple intents are present, choose the one explicitly requested last.
        
        Few-shot examples:
        - User (Italian): Spiegami MQTT → QA_TOOL
        - User (Italian): Crea flashcards su MQTT → FLASHCARD_TOOL
        - User (English): Make study flashcards for Edge computing → FLASHCARD_TOOL
        - User (Spanish): ¿Cuál es la diferencia entre Edge y Fog? → QA_TOOL
        - User (French): Explique-moi HTTPS → QA_TOOL
        - User (German): Erstelle Lernkarten über RAM und ROM → FLASHCARD_TOOL
        
        Respond ONLY with one of: QA_TOOL, FLASHCARD_TOOL, QUIZ_TOOL. No extra text, punctuation, or explanation.
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
            prompt
            | LLM().bind(temperature=0.0)
            | StrOutputParser()
    )

    try:
        response = chain.invoke({"input": user_query, "language": language_hint})
        logger.info("Invio messaggi al modello LLM...")

        text = response.strip().upper() #.content
        logger.info("Risposta grezza del modello: %s", text)

        match = re.search(r"(QA_TOOL|FLASHCARD_TOOL|QUIZ_TOOL)", text)
        if match:
            tool = match.group(1)
            logger.info("Tool selezionato: %s", tool)
            return tool

        logger.warning("Nessuna corrispondenza valida trovata nel testo: %s", text)
        logger.info("Default → QA_TOOL")

        return "QA_TOOL"
    except Exception as error:
        logger.error("Errore durante il routing: %s", str(error))
        logger.debug("Traceback completo:", exc_info=True)
        return "QA_TOOL"