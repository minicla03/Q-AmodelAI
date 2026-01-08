import asyncio
import sys
import os
import time

import ollama
from dotenv import load_dotenv


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.append(project_root)

data_path = os.path.join(project_root, "evaluation", "tool_eval","data")

base_env = os.path.join(project_root, ".env")
local_env = os.path.join(project_root, "evaluation", ".env.local")

load_dotenv(base_env)
load_dotenv(local_env, override=True)

import logging

logger = logging.getLogger(__name__)

from rag_logic.ingestion.ingestion import IngestionFlow
from rag_logic.tools.QATool import QATool
from rag_logic.utils import detect_language_from_query

from evaluation.tool_eval.qa_tool.qa_testset import TEST_CASES
from evaluation.tool_eval.qa_tool.metrics import custom_metrics
from evaluation.tool_eval.qa_tool.report_gen import generate_html_results

from deepeval import evaluate
from deepeval.models import OllamaModel
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric
)

class RateLimitedOllamaModel(OllamaModel):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)
        self.semaphore = asyncio.Semaphore(1)

    async def a_generate(self, prompt: str, schema=None):
        async with self.semaphore:
            client = ollama.AsyncClient(host=self.base_url)

            # Parametri per forzare il JSON se richiesto
            kwargs = {}
            if schema:
                kwargs["format"] = "json"

            response = await client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                **kwargs
            )

            content = response['message']['content']

            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]

            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            if schema:
                return schema.model_validate_json(content), 0.0

            return content, 0.0

CONFIGS = [
    {"summary": None},
    {"summary": True},
]


def evaluate_qa_tool(dataset, retrieval):
    results = []
    qa_tool = QATool()

    ollama_model = RateLimitedOllamaModel(
        model="gpt-oss:120b-cloud",
        #base_url="http://localhost:11434"
    )

    metrics = [
        AnswerRelevancyMetric(model=ollama_model),
        ContextualPrecisionMetric(model=ollama_model),
        ContextualRecallMetric(model=ollama_model),
        ContextualRelevancyMetric(model=ollama_model),
        FaithfulnessMetric(model=ollama_model)
    ]

    for idx, test_case_data in enumerate(dataset):

        if idx==5 or idx==10:
            time.sleep(1800)

        for config in CONFIGS:

            try:
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
                )

                actual_output = output.get("ai_response", "")
                if isinstance(actual_output, dict):
                    actual_output = str(actual_output)

                label = "CON RIASSUNTO" if config["summary"] else "SENZA RIASSUNTO"
                print(f"\n[{idx + 1}] {label}")
                print(f"Q: {user_query}")
                print(f"A: {actual_output[:150]}...")
                print("-" * 40)

                raw_sources = output.get("docs_source", [])
                retrieval_context = []
                for item in raw_sources:
                    if isinstance(item, dict):
                        retrieval_context.append(item.get("document_content", ""))
                    elif hasattr(item, "page_content"):
                        retrieval_context.append(item.page_content)
                    else:
                        retrieval_context.append(str(item))

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

                deepeval_res = evaluate([llm_test_case], metrics=metrics)

                results.append({
                    "query": user_query,
                    "summary_used": config["summary"] is not None,
                    "summary_label": "Con Riassunto" if config["summary"] else "Senza Riassunto",
                    "actual_output": actual_output,
                    "deepeval_result": deepeval_res,
                    "custom_metric_result": custom_res,
                })

                print(f" -> Elaborato caso {idx + 1} [Summary={config['summary']}]")
            except Exception as e:
                print(f"\n!!! ERRORE CRITICO DURANTE IL CASO {idx + 1} !!!")
                print(f"Errore: {e}")
                print("Interruzione forzata. Salvataggio dei risultati parziali ottenuti finora...")
                return results
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