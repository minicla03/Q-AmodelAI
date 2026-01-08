import unittest
from unittest.mock import patch, MagicMock
from langchain_core.messages import SystemMessage, HumanMessage
from rag_logic.tools.SummarizerTool import summary_agent

class TestSummaryAgent(unittest.TestCase):

    @patch("rag_logic.agents.summarizer_agent.ChatOllama")  # mockiamo ChatOllama
    def test_summary_agent_basic(self, MockChatOllama):
        mock_llm_instance = MockChatOllama.return_value
        mock_response = MagicMock()
        mock_response.content = "Questo è un riassunto fittizio."
        mock_llm_instance.invoke.return_value = mock_response

        conversation_history = [
            HumanMessage(content="Ciao, puoi aiutarmi a capire Python?"),
            SystemMessage(content="Certo, di cosa hai bisogno?"),
            HumanMessage(content="Vorrei imparare le funzioni.")
        ]

        summary = summary_agent(conversation_history, language_hint="italian")

        self.assertEqual(summary, "Questo è un riassunto fittizio.")

        mock_llm_instance.invoke.assert_called_once()
        messages_passed = mock_llm_instance.invoke.call_args[0][0]
        self.assertIsInstance(messages_passed[0], SystemMessage)
        self.assertIsInstance(messages_passed[1], HumanMessage)
        self.assertIn("HumanMessage: Ciao, puoi aiutarmi a capire Python?", messages_passed[1].content)

    @patch("rag_logic.agents.summarizer_agent.ChatOllama")
    def test_summary_agent_empty_history(self, MockChatOllama):
        mock_llm_instance = MockChatOllama.return_value
        mock_response = MagicMock()
        mock_response.content = "Nessuna conversazione da riassumere."
        mock_llm_instance.invoke.return_value = mock_response

        summary = summary_agent([], language_hint="italian")
        self.assertEqual(summary, "Nessuna conversazione da riassumere.")

if __name__ == "__main__":
    unittest.main()
