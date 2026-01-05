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

import json
from html import escape


def generate_html_results(results: list, output_file="results.html"):
    """
    Genera un file HTML con i risultati di valutazione QA.

    Args:
        results (list): Lista di dizionari con i risultati.
        output_file (str): Nome del file HTML da salvare.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Valutazione QA</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 10px; text-align: left; vertical-align: top; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .json-block { font-family: monospace; white-space: pre-wrap; background: #eee; padding: 5px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>Risultati Valutazione QA</h1>
        <table>
            <thead>
                <tr>
                    <th>Query</th>
                    <th>Summary usato</th>
                    <th>Toon format</th>
                    <th>Deepeval Result</th>
                    <th>Custom Metric Result</th>
                </tr>
            </thead>
            <tbody>
    """

    for entry in results:
        deepeval_html = escape(json.dumps(entry["deepeval_result"], indent=2))
        custom_html = escape(json.dumps(entry["custom_metric_result"], indent=2))
        html_content += f"""
            <tr>
                <td>{escape(entry['query'])}</td>
                <td>{'✅' if entry['summary_used'] else '❌'}</td>
                <td>{escape(entry['toon_format'])}</td>
                <td><div class="json-block">{deepeval_html}</div></td>
                <td><div class="json-block">{custom_html}</div></td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"File HTML generato con successo: {output_file}")

def evaluate_qa_tool(dataset, retrieval):

    deepeval_results = []
    custom_metric_results = []
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

            processed_query = {
                "user_query": test_case_data["query"],
                "summary": test_case_data.get("summary") if config["summary"] else "",
            }

            language_hint = detect_language_from_query(test_case_data["query"])

            output = qa_tool.execute(
                retriever=retrieval,
                query=processed_query,
                toon_format=config["toon_format"]
            )

            custom_metric_results.append(
                custom_metrics(
                    output["ai_response"],
                    test_case_data["expected_answer"],
                    language=language_hint
                )
            )

            llm_test_case = LLMTestCase(
                input=processed_query["user_query"] + "\nSummary:" + (processed_query["summary"]),
                actual_output=output["ai_response"],
                retrieval_context=[doc.page_content for doc in output.get("docs_source", [])],
                expected_output=test_case_data["expected_answer"]
            )

            deepeval_results.append(evaluate([llm_test_case], metrics=metrics))

    for idx, (llm_test_case, processed_query, config, custom_metric_result) in enumerate(deepeval_results):
        results.append({
            "query": processed_query["query"],
            "summary_used": processed_query["summary"] is not None,
            "toon_format": config["toon_format"],
            "deepeval_result": deepeval_results[idx],
            "custom_metric_result": custom_metric_result,
        })

    return results

def start_qa_evaluation():
    dataset = TEST_CASES

    try:
        ingestor = IngestionFlow("691642bdbaec0c4aae000526")
        ingestor.add_documents_from_folder(data_path) if not ingestor.reload_vectorstore() else None
        retrieval = ingestor.retriever_vs
    except (FileNotFoundError, ValueError) as e:
        logger.error(e, exc_info=True)
        exit(1)

    logger.info("Inizio valutazione su test set...\n")

    results = evaluate_qa_tool(dataset, retrieval)
    generate_html_results(results, "valutazione_qa.html")
