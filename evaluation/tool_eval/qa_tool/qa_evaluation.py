from dotenv import load_dotenv
import os

load_dotenv("../../.env.local")
print(os.getenv("OPENAI_API_KEY"))

base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_path, "..", "data")
data_path = os.path.abspath(data_path)

import logging

logger = logging.getLogger(__name__)

from rag_logic.ingestion.ingestion import IngestionFlow
from rag_logic.tools.QATool import QATool
from rag_logic.utils import detect_language_from_query

from evaluation.tool_eval.qa_tool.qa_testset import TEST_CASES
from evaluation.tool_eval.qa_tool.metrics import custom_metrics
from evaluation.tool_eval.qa_tool.report_gen import generate_html_results

from deepeval import evaluate
from deepeval.models import OllamaModel, DeepSeekModel
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric
)

CONFIGS = [
    {"summary": None, "toon_format": False},
    {"summary": True, "toon_format": False},
    #{"summary": None, "toon_format": True},
    #{"summary": True, "toon_format": True},
]


def evaluate_qa_tool(dataset, retrieval):
    results = []
    qa_tool = QATool()

    ollama_model = DeepSeekModel(model="deepseek-chat", api_key=os.getenv("OPENAI_API_KEY"))

    metrics = [
        AnswerRelevancyMetric(model=ollama_model),
        ContextualPrecisionMetric(model=ollama_model),
        ContextualRecallMetric(model=ollama_model),
        ContextualRelevancyMetric(model=ollama_model),
        FaithfulnessMetric(model=ollama_model)
    ]

    for idx, test_case_data in enumerate(dataset):
        for config in CONFIGS:

            user_query = test_case_data["query"]
            summary_text = test_case_data.get("summary") if config["summary"] else ""

            processed_query = {
                "user_query": user_query,
                "summary": summary_text,
            }

            language_hint = detect_language_from_query(user_query)

            output = qa_tool.execute(
                retriever=retrieval,
                query=processed_query,
                toon_format=config["toon_format"]
            )

            actual_output = output.get("ai_response", "")
            if isinstance(actual_output, dict):
                actual_output = str(actual_output)

            retrieval_context = [doc.page_content for doc in output.get("docs_source", [])]

            custom_res = custom_metrics(
                actual_output,
                test_case_data["expected_answer"],
                language=language_hint
            )

            input_text = user_query
            if summary_text:
                input_text += f"\nSummary: {summary_text}"

            llm_test_case = LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                retrieval_context=retrieval_context,
                expected_output=test_case_data["expected_answer"]
            )

            deepeval_res = evaluate([llm_test_case], metrics=metrics, print_results=True)

            results.append({
                "query": user_query,
                "summary_used": config["summary"] is not None,
                "toon_format": config["toon_format"],
                "deepeval_result": deepeval_res,
                "custom_metric_result": custom_res,
            })

            print(f" -> Elaborato caso {idx + 1} [Summary={config['summary']}]")

    return results


def start_qa_evaluation():
    dataset = TEST_CASES

    try:
        ingestor = IngestionFlow("691642bdbaec0c4aae000526")

        if not ingestor.reload_vectorstore():
            logger.info("Vectorstore non trovato o vuoto, indicizzazione documenti...")
            ingestor.add_documents_from_folder(data_path)
        else:
            logger.info("Vectorstore caricato con successo.")

        retrieval = ingestor.retriever_vs

    except Exception as e:
        logger.error(f"Errore inizializzazione ingestion: {e}", exc_info=True)
        return

    logger.info("Inizio valutazione su test set...\n")

    results = evaluate_qa_tool(dataset, retrieval)
    generate_html_results(results, "valutazione_qa.html")


if __name__ == "__main__":
    start_qa_evaluation()