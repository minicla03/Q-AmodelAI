import logging
from deepeval import evaluate
from deepeval.metrics import ExactMatchMetric
from deepeval.test_case import LLMTestCase

from evaluation.tool_selection_eval.router_testset import TEST_ROUTER_DATASET, COMPLEX_CASES
from rag_logic.agents.routing_agent import router_agent
from rag_logic.utils import detect_language_from_query

logger = logging.getLogger(__name__)


def generate_test_result_html(results, aggregate_metrics, aggregate_metrics_tool, filename="router_test_report_nv.html"):

    total_tests = aggregate_metrics["total_tests"]
    total_success = aggregate_metrics["total_success"]
    overall_success_rate = aggregate_metrics["overall_success_rate"]

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Router Test Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h2 { color: #333; }
            h3 { color: #555; margin-bottom: 5px; }
            table { border-collapse: collapse; width: 80%; margin-bottom: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .success { color: green; font-weight: bold; }
            .failure { color: red; font-weight: bold; }
        </style>
    </head>"""

    html_content += f"""
    <body>
        <h2>Router Test Report</h2>
        <h3>Summary</h3>
        <p>Total Tests: {total_tests}</p>
        <p>Total Successes: {total_success}</p>
        <p>Overall Success Rate: {overall_success_rate:.2f}%</p>
        <hr>
    """

    html_content += "<h3>Aggregated Metrics per Tool</h3>"
    html_content += "<table><tr><th>Tool</th><th>Total Tests</th><th>Successes</th><th>Success Rate</th></tr>"
    for tool, stats in aggregate_metrics_tool.items():
        html_content += f"<tr><td>{tool}</td><td>{stats['total']}</td><td>{stats['success']}</td><td>{stats['success_rate']:.2f}%</td></tr>"
    html_content += "</table><hr>"

    html_content += f"""
    <h3>Hyperparameters</h3>
    <ul>
        <li>Model: gpt-oss:20b-cloud</li>
        <li>Temperature: 0.1</li>
        <li>Top-p: 0.9</li>
        <li>Num Context Tokens: 4096</li>
        <li>Max Tokens: 300</li>
        <li>Repeat Penalty: 1.1</li>
        <li>Toon Format Options: False, True</li>
    </ul>
    <hr>"""

    for query, info in results.items():
        expected = info['expected']
        html_content += f"<h3>Query: {query}</h3>"
        html_content += f"<p><strong>Expected Output:</strong> {expected}</p>"

        for toon_format, res in info['results_per_toon_format'].items():
            test_result = res['match'].test_results[0]  # prende il primo TestResult
            html_content += f"<h4>Toon format = {toon_format}</h4>"
            html_content += f"<p><strong>Actual Output:</strong> {test_result.actual_output}</p>"
            result_class = "success" if test_result.success else "failure"
            html_content += f"<p><strong>Result:</strong> <span class='{result_class}'>{'Success' if test_result.success else 'Failure'}</span></p>"

            html_content += """
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Score</th>
                    <th>Threshold</th>
                    <th>Success</th>
                    <th>Details</th>
                </tr>
            """
            for metric in test_result.metrics_data:
                metric_class = "success" if metric.success else "failure"
                html_content += f"""
                <tr>
                    <td>{metric.name}</td>
                    <td>{metric.score}</td>
                    <td>{metric.threshold}</td>
                    <td class="{metric_class}">{'✅' if metric.success else '❌'}</td>
                    <td>{metric.reason}</td>
                </tr>
                """
            html_content += "</table>"
            html_content += f"<p><strong>Conversational:</strong> {test_result.conversational} | " \
                            f"<strong>Multimodal:</strong> {test_result.multimodal}</p><hr>"

    html_content += "</body></html>"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Report salvato in {filename}")

def aggregate_metrics_calculate(results):
    """
    Calcola metriche aggregate dal dict dei risultati.
    Restituisce un dict con total_tests, total_success e overall_success_rate.
    """
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

    print(type(results))  # <class 'dict'>
    print(list(results.keys())[0])  # Mostra la prima query
    print(results[list(results.keys())[0]])  # Mostra il contenuto del primo item

    """for query, info in results.items():
        print(f"Query: {query}")
        print(f"Expected: {info['expected']}")
        for toon_format, res in info['results_per_toon_format'].items():
            print(f"  Toon format={toon_format}: Predicted={res['predicted']}, Match={res['match']}")
        print("-" * 60)"""

    aggregate_metrics = aggregate_metrics_calculate(results)
    aggregate_metrics_tool = aggregate_metrics_per_tool(results)
    generate_test_result_html(results, aggregate_metrics, aggregate_metrics_tool)

if __name__ == '__main__':
    start_evaluate_router()