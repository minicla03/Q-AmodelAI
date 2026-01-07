import time
import logging
import dotenv

dotenv.load_dotenv(".env")

from tool_selection_eval.router_evaluation import start_evaluate_router
from tool_eval.qa_tool.qa_evaluation import start_qa_evaluation
from summary_generation.summarizer_evaluation import start_evaluation_summarizer

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    start_evaluate_router()
    time.sleep(1800)
    start_evaluation_summarizer()
    time.sleep(1800)
    start_qa_evaluation()

