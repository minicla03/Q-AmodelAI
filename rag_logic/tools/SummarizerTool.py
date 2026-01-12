import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from rag_logic.llm.LLM import LLM
from rag_logic.tools.ITool import IToolStrategy

# Configura logger di base
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class SummarizerTool(IToolStrategy):

    def execute(self, retriever, query: dict):

        conversation_history = query.get("conversation_history", [])

        logger.info("Avvio generazione sommario...")
        logger.info("Lunghezza conversazione: %d messaggi", len(conversation_history))

        language = self._detect_language_from_query(conversation_history[0])

        # Converte la conversazione in testo
        formatted_lines = []
        for msg in conversation_history:
            if hasattr(msg, "content"):
                role = "User" if msg.type == "human" else "AI"
                formatted_lines.append(f"{role}: {msg.content}")
            elif isinstance(msg, dict):
                role = msg.get("role", "Unknown")
                content = msg.get("content", "")
                formatted_lines.append(f"{role}: {content}")
            else:
                formatted_lines.append(str(msg))

        conv_text = "\n".join(formatted_lines)
        if not conv_text.strip():
            logger.warning("Cronologia vuota. Nessun sommario generato.")
            return {}

        logger.info("Conversazione convertita in testo. Lunghezza caratteri: %d", len(conv_text))

        template = """
            You are a chat summarization agent. 
            Your task is to analyze the entire conversation history between the user and the assistant 
            and produce a clear, concise summary capturing the essential information.\n\n
    
            Guidelines:\n
            - Write in {language}.\n
            - Focus on the main topics discussed, the user’s goals, and any specific requests or constraints.\n
            - Omit greetings, filler phrases, or unrelated small talk.\n
            - Maintain a neutral and factual tone.\n
            - If the conversation includes technical explanations, summarize the key points without unnecessary detail.\n\n
    
            Your output should be a short paragraph (5–7 lines) that provides enough context
            for another model to understand what the conversation was about and continue it smoothly.\n\n
            
            conversation history to summarize:
            {conversation_text}
        """

        prompt = ChatPromptTemplate.from_template(template)

        chain = (
                prompt
                | LLM().bind(temperature=0.0)
                | StrOutputParser()
        )

        try:
            logger.info("Invio messaggi al modello LLM...", )
            summary = chain.invoke({
                "conversation_text": conv_text,
                "language": language})
            logger.debug("Sommario:\n%s", summary)
            logger.info("Sommario generato correttamente. Lunghezza caratteri: %d %s", len(summary), type(summary))
            return summary.strip()
        except Exception as e:
            logger.error(f"Errore Summary: {e}")
            return ""


