from fastapi.testclient import TestClient

from backend.src.main import app


client = TestClient(app)


def test_health_endpoint_reports_engine_mode():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "engineMode" in response.json()


def test_websocket_submit_query_streams_expected_events():
    with client.websocket_connect("/ws/rag") as websocket:
        websocket.send_json({"type": "submit_query", "query": "What is RAG?"})

        first = websocket.receive_json()
        assert first["type"] == "run_started"
        assert first["query"] == "What is RAG?"

        event_types = {first["type"]}
        while "run_completed" not in event_types:
            event = websocket.receive_json()
            event_types.add(event["type"])

        assert "query_rewritten" in event_types
        assert "documents_retrieved" in event_types
        assert "grading_completed" in event_types
