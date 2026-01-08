import logging
import re
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from rag_logic.agents.AgentState import AgentState
from rag_logic.llm.LLM import LLM
from rag_logic.tools.ITool import ContextFactory

logger = logging.getLogger(__name__)


class PlannerAgent:

    MAX_STEPS = 5
    SUMMARY_THRESHOLD = 10

    def __init__(self,
                 retriever: Any,
                 language_hint: str):

        self.retriever = retriever
        self.language_hint=language_hint

    def _planner_agent(self, state: AgentState) -> str:

        user_query=state.query["user_query"]
        logger.info("Avvio router_agent per query: %s", user_query)

        template = """
            You are an intelligent task router for a Retrieval-Augmented Generation (RAG) system.
            Your job is to analyze the user's request and decide which function should be executed.
            
            User Query: "{input}"
            
            Available functions:
            1. QA_TOOL → Answers a question based on the context retrieved from documents.
            2. FLASHCARD_TOOL → Generates study flashcards (question/answer pairs) from the content.
            3. QUIZ_TOOL → Generates quiz from the content.
            4. SUMMARY_TOOL → generate conversation summary
            5. STOP → finish the process
            
            Guidelines:
            - Use the language of the user's query if detectable, otherwise fallback to {language_hint}.
            - If the query asks for explanations, summaries, or answers → QA_TOOL.
            - If the query asks to generate flashcards → FLASHCARD_TOOL.
            - If the query asks to generate quiz questions → QUIZ_TOOL.
            - If multiple intents are present, choose the one explicitly requested last.
            - PRIORITY RULE: If "{msg_count}" > "{threshold}" AND "SUMMARY_TOOL" is NOT in "Previous actions taken", you MUST choose SUMMARY_TOOL immediately, regardless of the user query.
            - If "SUMMARY_TOOL" was just executed, proceed to handle the user's actual query (e.g., QA_TOOL).
            - If user explicitly asks for a summary → SUMMARY_TOOL.
            
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
            response =response = chain.invoke({
                "input": user_query,
                "history": ", ".join(state.history),
                "msg_count": state.message_count,
                "threshold": self.SUMMARY_THRESHOLD
            })
            logger.info("Invio messaggi al modello LLM...")

            text = response.strip().upper()
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

    def execute_agent(self, query: str, conversation_history: list = None, message_count: int = 0) -> AgentState:
        state = AgentState(query=query, language_hint=self.language_hint, message_count=message_count)
        state.retriever = self.retriever

        while not state.done and state.steps < self.MAX_STEPS:

            logger.info("Step %d: Pianificazione prossima azione...", state.steps + 1)
            action = self._planner_agent(state)
            logger.info("Planner ha scelto: %s", action)

            if action == "STOP":
                state.done = True
                break

            if action == "SUMMARY_TOOL":

                is_explicit_request = "riassun" in query.lower() or "summar" in query.lower()
                if not is_explicit_request:
                    logger.info("Auto-summary completato. Continuo per rispondere all'utente...")
                    state.done = False
                else:
                    state.done = True


            if action in ["QA_TOOL", "FLASHCARD_TOOL", "QUIZ_TOOL"]:
                context = ContextFactory.create(action)
                if context is None:
                    logger.warning("Tool '%s' non trovato, passo al prossimo", action)
                    state.done = True
                    continue

                query_input = {"query": state.query}
                if action == "SUMMARY_TOOL" and conversation_history is not None:
                    query_input = {"conversation_history": conversation_history}

                result = context.execute(
                    retriever=state.retriever,
                    query=query_input,
                    language=state.language_hint
                )

                if "docs" in result:
                    state.docs.extend(result["docs"])
                if "answer" in result:
                    state.answer = result["answer"]
                if "summary" in result:
                    state.summary = result["summary"]

                if action in ["FLASHCARD_TOOL", "QUIZ_TOOL", "SUMMARY_TOOL"]:
                    state.done = True

            elif action == "STOP":
                state.done = True

            state.history.append(action)
            state.steps += 1

        logger.info("Processo completato. Azioni eseguite: %s", state.history)
        return state