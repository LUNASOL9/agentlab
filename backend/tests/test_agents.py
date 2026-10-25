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


def create(client: TestClient, name: str) -> dict[str, Any]:
    response = client.post("/api/agents", json={"name": name})
    assert response.status_code == 201
    return response.json()


def test_list_agents(client: TestClient) -> None:
    create(client, "a")
    create(client, "b")

    response = client.get("/api/agents")

    assert response.status_code == 200
    assert [agent["name"] for agent in response.json()] == ["a", "b"]


def test_list_agents_with_pagination(client: TestClient) -> None:
    for name in ["a", "b", "c", "d"]:
        create(client, name)

    response = client.get("/api/agents", params={"offset": 1, "limit": 2})

    assert response.status_code == 200
    assert [agent["name"] for agent in response.json()] == ["b", "c"]


def test_list_agents_rejects_too_large_limit(client: TestClient) -> None:
    response = client.get("/api/agents", params={"limit": 1000})

    assert response.status_code == 422


def test_update_agent_changes_only_sent_fields(client: TestClient) -> None:
    agent = create(client, "before")

    response = client.patch(f"/api/agents/{agent['id']}", json={"name": "after"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "after"
    assert body["temperature"] == agent["temperature"]  # 보내지 않은 필드는 그대로예요.
    assert client.get(f"/api/agents/{agent['id']}").json()["name"] == "after"


def test_update_agent_not_found(client: TestClient) -> None:
    response = client.patch("/api/agents/999", json={"name": "x"})

    assert response.status_code == 404


def test_delete_agent(client: TestClient) -> None:
    agent = create(client, "to-delete")

    response = client.delete(f"/api/agents/{agent['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/agents/{agent['id']}").status_code == 404


def test_delete_agent_not_found(client: TestClient) -> None:
    response = client.delete("/api/agents/999")

    assert response.status_code == 404


# [과제 5-1] 주석을 풀고 ____를 채워요.
# def test_create_agent_duplicate_name(client: TestClient) -> None:
#     first = client.post("/api/agents", json=AGENT)
#     assert first.status_code == 201
#
#     second = client.post("/api/agents", json=____)  # 똑같은 내용을 한 번 더 보내요.
#
#     assert second.status_code == ____
