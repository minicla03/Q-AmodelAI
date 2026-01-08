import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)

from dotenv import load_dotenv

import logging
import json

from deepeval.dataset import Golden, EvaluationDataset
from deepeval.evaluate import evaluate
from deepeval.test_case import LLMTestCase

from evaluation.summary_generation import summary_metrics
from evaluation.summary_generation.html_report_gen import generate_html_report
from rag_logic.tools.SummarizerTool import summary_agent
from rag_logic.utils import detect_language_from_query

from summary_testset import TEST_CASE

logger = logging.getLogger(__name__)


def evaluate_summarizer(test_dataset):

    results = []

    for idx, golden in enumerate(test_dataset.goldens):

        conversation_history_list = json.loads(golden.input)
        expected_summary = golden.expected_output

        language_hint = detect_language_from_query(conversation_history_list[0]["content"])
        logger.info(f"Language hint: {language_hint}")

        predicted_summary = summary_agent(conversation_history_list, language_hint)

        logger.info("Avvio valutazione sul summarizer...")

        context_data = [msg["content"] for msg in conversation_history_list]

        classic_metric_result = summary_metrics.classic_metric(expected_summary, predicted_summary)

        test_case = LLMTestCase(
            input=golden.input,
            actual_output=predicted_summary,
            expected_output=expected_summary,
            context=context_data,
            retrieval_context=context_data
        )

        deepeval_result = evaluate(
            test_cases=[test_case],
            metrics=summary_metrics.get_list_deep_eval_metrics(),
        )

        results.append({
            "test_index": idx,
            "predicted_summary": predicted_summary,
            "expected_summary": expected_summary,
            "deepeval": deepeval_result,
            "classic_metrics": classic_metric_result
        })

    return results

def _create_golden(dataset):
    goldens = []
    for item in dataset:
        goldens.append(
            Golden(
                input=json.dumps(item["conversation_history"], ensure_ascii=False),
                expected_output = item["expected_summary"]
            )
        )
    return goldens

def start_evaluation_summarizer():
    load_dotenv(dotenv_path="evaluation/.env.local", override=True)

    tests = TEST_CASE
    dataset= EvaluationDataset(goldens=_create_golden(tests))
    # dataset.push(alias="MessageSummarizer Dataset")
    results = evaluate_summarizer(dataset)
    generate_html_report(results, output_path="summarizer_report.html")

if __name__ == "__main__":
    start_evaluation_summarizer()