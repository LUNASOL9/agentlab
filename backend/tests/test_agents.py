from fastapi.testclient import TestClient

AGENT = {
    "name": "math-tutor",
    "description": "수학 문제를 단계별로 풀어주는 에이전트",
    "model": "mock",
    "system_prompt": "You are a patient math tutor.",
    "temperature": 0.2,
}


def test_create_agent(client: TestClient) -> None:
    response = client.post("/api/agents", json=AGENT)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["name"] == "math-tutor"
    assert body["temperature"] == 0.2
    assert "created_at" in body


def test_create_agent_uses_defaults(client: TestClient) -> None:
    response = client.post("/api/agents", json={"name": "minimal"})

    assert response.status_code == 201
    body = response.json()
    assert body["model"] == "mock"
    assert body["temperature"] == 0.7
    assert body["description"] is None


def test_create_agent_rejects_invalid_temperature(client: TestClient) -> None:
    response = client.post("/api/agents", json={**AGENT, "temperature": 1.5})

    # Spring은 검증 실패에 400을 주지만, FastAPI는 422 Unprocessable Entity를 줘요.
    assert response.status_code == 422


def test_create_agent_rejects_empty_name(client: TestClient) -> None:
    response = client.post("/api/agents", json={**AGENT, "name": ""})

    assert response.status_code == 422


def test_get_agent(client: TestClient) -> None:
    created = client.post("/api/agents", json=AGENT).json()

    response = client.get(f"/api/agents/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_agent_not_found(client: TestClient) -> None:
    response = client.get("/api/agents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Agent not found: id=999"}


# [과제 5-1] 주석을 풀고 ____를 채워요.
# def test_create_agent_duplicate_name(client: TestClient) -> None:
#     first = client.post("/api/agents", json=AGENT)
#     assert first.status_code == 201
#
#     second = client.post("/api/agents", json=____)  # 똑같은 내용을 한 번 더 보내요.
#
#     assert second.status_code == ____
