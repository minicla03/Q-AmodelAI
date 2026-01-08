import pytest
from unittest.mock import MagicMock
from rag_logic.agents.PlannerAgent import router_agent

def _mock_llm(response_text):
    mock_llm_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.content = response_text
    mock_llm_instance.invoke.return_value = mock_response
    return mock_llm_instance

@pytest.mark.parametrize(
    "user_input, mock_response, expected_tool",
    [
        ("Crea delle flashcard su MQTT.", "FLASHCARD_TOOL", "FLASHCARD_TOOL"),
        ("Genera un quiz sul protocollo TCP/IP.", "QUIZ_TOOL", "QUIZ_TOOL"),
        ("Spiegami come funziona il protocollo MQTT.", "QA_TOOL", "QA_TOOL"),
        # Caso di output non normalizzato
        ("Genera un quiz sul protocollo TCP/IP.", "The correct tool is quiz_tool.", "QUIZ_TOOL"),
    ]
)
def test_router_agent_routing(monkeypatch, user_input, mock_response, expected_tool):
    mock_llm_instance = _mock_llm(mock_response)

    monkeypatch.setattr("rag_logic.agents.routing_agent.ChatOllama", lambda **_: mock_llm_instance)

    result = router_agent(user_input)
    assert result.upper() == expected_tool.upper()
