from fastapi.testclient import TestClient


# client는 conftest.py의 fixture가 넣어줘요. MockMvc처럼 서버 없이 API를 호출해요.
def test_read_root(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, LUNA!"}
