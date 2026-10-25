"""1단계 과제 2~4용 테스트예요.

과제를 구현한 뒤, 해당 테스트 위의 `@pytest.mark.skip(...)` 줄을 지우고
`uv run pytest`로 통과하는지 확인하세요. 과제를 다 끝내면 이 파일의 테스트를
test_agents.py로 옮기고 이 파일은 지워도 돼요.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient


def create(client: TestClient, name: str) -> dict[str, Any]:
    response = client.post("/api/agents", json={"name": name})
    assert response.status_code == 201
    return response.json()


# --- 과제 2: 목록 조회 ---


@pytest.mark.skip(reason="과제 2: GET /api/agents 구현 후 이 줄을 지우세요")
def test_list_agents(client: TestClient) -> None:
    create(client, "a")
    create(client, "b")

    response = client.get("/api/agents")

    assert response.status_code == 200
    assert [agent["name"] for agent in response.json()] == ["a", "b"]


@pytest.mark.skip(reason="과제 2: GET /api/agents 구현 후 이 줄을 지우세요")
def test_list_agents_with_pagination(client: TestClient) -> None:
    for name in ["a", "b", "c", "d"]:
        create(client, name)

    response = client.get("/api/agents", params={"offset": 1, "limit": 2})

    assert response.status_code == 200
    assert [agent["name"] for agent in response.json()] == ["b", "c"]


@pytest.mark.skip(reason="과제 2: GET /api/agents 구현 후 이 줄을 지우세요")
def test_list_agents_rejects_too_large_limit(client: TestClient) -> None:
    response = client.get("/api/agents", params={"limit": 1000})

    assert response.status_code == 422


# --- 과제 3: 부분 수정 ---


@pytest.mark.skip(reason="과제 3: PATCH /api/agents/{agent_id} 구현 후 이 줄을 지우세요")
def test_update_agent_changes_only_sent_fields(client: TestClient) -> None:
    agent = create(client, "before")

    response = client.patch(f"/api/agents/{agent['id']}", json={"name": "after"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "after"
    assert body["temperature"] == agent["temperature"]  # 보내지 않은 필드는 그대로예요.
    assert client.get(f"/api/agents/{agent['id']}").json()["name"] == "after"


@pytest.mark.skip(reason="과제 3: PATCH /api/agents/{agent_id} 구현 후 이 줄을 지우세요")
def test_update_agent_not_found(client: TestClient) -> None:
    response = client.patch("/api/agents/999", json={"name": "x"})

    assert response.status_code == 404


# --- 과제 4: 삭제 ---


@pytest.mark.skip(reason="과제 4: DELETE /api/agents/{agent_id} 구현 후 이 줄을 지우세요")
def test_delete_agent(client: TestClient) -> None:
    agent = create(client, "to-delete")

    response = client.delete(f"/api/agents/{agent['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/agents/{agent['id']}").status_code == 404


@pytest.mark.skip(reason="과제 4: DELETE /api/agents/{agent_id} 구현 후 이 줄을 지우세요")
def test_delete_agent_not_found(client: TestClient) -> None:
    response = client.delete("/api/agents/999")

    assert response.status_code == 404
