import logging
from deepeval import evaluate
from deepeval.metrics import ExactMatchMetric
from deepeval.test_case import LLMTestCase

from evaluation.tool_selection_eval.router_testset import TEST_ROUTER_DATASET, COMPLEX_CASES
from evaluation.tool_selection_eval.gen_report import generate_test_result_html
from rag_logic.agents.PlannerAgent import router_agent
from rag_logic.utils import detect_language_from_query

logger = logging.getLogger(__name__)


def aggregate_metrics_calculate(results):

    total_tests = 0
    total_success = 0
    for info in results.values():
        for res in info['results_per_toon_format'].values():
            test_result = res['match'].test_results[0]
            total_tests += 1
            if test_result.success:
                total_success += 1
    overall_success_rate = (total_success / total_tests) * 100 if total_tests > 0 else 0.0
    return {
        "total_tests": total_tests,
        "total_success": total_success,
        "overall_success_rate": overall_success_rate
    }

def aggregate_metrics_per_tool(results):
    """
    Calcola metriche aggregate per ciascun tool.
    Restituisce un dict {tool_name: {'total': int, 'success': int, 'success_rate': float}}
    """
    tool_stats = {}

    for info in results.values():
        expected_tool = info['expected']
        for toon_format, res in info['results_per_toon_format'].items():
            test_result = res['match'].test_results[0]

            if expected_tool not in tool_stats:
                tool_stats[expected_tool] = {'total': 0, 'success': 0}

            tool_stats[expected_tool]['total'] += 1
            if test_result.success:
                tool_stats[expected_tool]['success'] += 1

    # calcolo percentuale
    for tool, stats in tool_stats.items():
        stats['success_rate'] = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0.0

    return tool_stats

def evaluate_router(test_dataset):

    toon_format_options = [False]
    results = {}

    for item in test_dataset:

        query = item["query"]
        language_hint = detect_language_from_query(query)
        expected = item["expected_tool"]
        item_result = {}

        for toon_format in toon_format_options:

            predicted = router_agent(query, language_hint,)

            test_case = LLMTestCase(
                input=query,
                actual_output=predicted,
                expected_output=expected,
                #additional_metadata = log_hyperparameters
            )

            # Metrica: match esatto tra expected e predicted
            exact_match_metric = ExactMatchMetric()

            logger.info("Avvio valutazione DeepEval sul router...")
            result = evaluate(test_cases=[test_case], metrics=[exact_match_metric])
            item_result[toon_format] = {
                "predicted": predicted,
                "match": result
            }

            results[query] = {
                "expected": expected,
                "results_per_toon_format": item_result
            }

    return results

def start_evaluate_router():
    dataset = TEST_ROUTER_DATASET + COMPLEX_CASES
    results = evaluate_router(dataset)

    aggregate_metrics = aggregate_metrics_calculate(results)
    aggregate_metrics_tool = aggregate_metrics_per_tool(results)
    generate_test_result_html(results, aggregate_metrics, aggregate_metrics_tool)

if __name__ == '__main__':
    start_evaluate_router()