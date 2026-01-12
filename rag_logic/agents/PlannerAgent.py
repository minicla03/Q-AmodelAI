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

    def __init__(self, retriever: Any):

        self.retriever = retriever

    def _llm_router(self, state: AgentState) -> str:

        user_query=state.user_query
        logger.info("Avvio router_agent per query: %s", user_query)

        template = """
            You are an intelligent task router for a Retrieval-Augmented Generation (RAG) system.
            Your job is to analyze the user's request and decide which function should be executed.
            
            User Query: "{input}"
            Context/History: "{history}"
            
            Available functions:
            1. QA_TOOL → Answers a question based on the context retrieved from documents.
            2. FLASHCARD_TOOL → Generates study flashcards (question/answer pairs) from the content.
            3. QUIZ_TOOL → Generates quiz from the content.
            
            Guidelines:
            - Use the language of the user's query if detectable, otherwise fallback.
            - If the query asks for explanations, summaries, or answers → QA_TOOL.
            - If the query asks to generate flashcards → FLASHCARD_TOOL.
            - If the query asks to generate quiz questions → QUIZ_TOOL.
            - If multiple intents are present, choose the one explicitly requested last.
            
            Respond ONLY with one of: QA_TOOL, FLASHCARD_TOOL, QUIZ_TOOL. No extra text, punctuation, or explanation.
        """

        prompt = ChatPromptTemplate.from_template(template)

        chain = (
                prompt
                | LLM().bind(temperature=0.0)
                | StrOutputParser()
        )

        try:
            response = chain.invoke({
                "input": user_query,
                "history": ", ".join(state.history),
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

    def _plan_next_action(self, state: AgentState) -> str:
        query_lower = state.user_query.lower()

        if state.has_answer and state.steps > 0:
            if any(k in query_lower for k in ["riassumi", "summary", "sintesi"]):
                if not state.has_summary:
                    state.summary_reason = "explicit"
                    return "SUMMARY_TOOL"
                return "STOP"

        if (state.message_count >= self.SUMMARY_THRESHOLD
                and not state.has_summary and not state.has_answer):
            state.summary_reason = "implicit"
            return "SUMMARY_TOOL"

        return self._llm_router(state)

    def execute_agent(self, query: str, conversation_history: list = None, message_count: int = 0) -> AgentState:
        state = AgentState(user_query=query, message_count=message_count)
        state.retriever = self.retriever

        while not state.done and state.steps < self.MAX_STEPS:

            logger.info("Step %d: Pianificazione prossima azione...", state.steps + 1)

            # Plan
            action = self._plan_next_action(state)
            logger.info("Planner ha scelto: %s", action)

            # Execute
            if action == "STOP":
                state.done = True
                break

            context = ContextFactory.create(action)
            if context is None:
                logger.warning("Tool '%s' non trovato, passo al prossimo", action)
                state.done = True
                continue

            tool_input = {}
            if action == "SUMMARY_TOOL":
                tool_input = {"conversation_history": conversation_history}
            else:
                tool_input = {
                    "user_query": state.user_query,
                    "summary": state.summary
                }

            try:
                result = context.execute(
                    retriever=state.retriever,
                    query=tool_input
                )
            except Exception as e:
                logger.error(f"Error executing {action}: {e}")
                state.done = True
                break

            # Observe
            state.history.append(action)

            if "docs" in result:
                state.docs.extend(result["docs"])
                state.explanation = result["docs_source"]
            if "ai_response" in result:
                state.answer = result["ai_response"]
                state.explanation = result["docs_source"]
                state.has_answer = True
            if "summary" in result:
                state.summary = result["summary"]
                state.has_summary = True

            if action == "SUMMARY_TOOL":
                if state.summary_reason == "implicit":
                    logger.info("Implicit summary done. Proceeding to answer user query.")
                else:
                    state.done = True

            if action in ["QA_TOOL", "FLASHCARD_TOOL", "QUIZ_TOOL"] and state.has_answer:
                state.done = True

            state.steps += 1

        logger.info("Processo completato. Azioni eseguite: %s", state.history)
        return state