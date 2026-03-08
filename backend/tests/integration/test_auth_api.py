import unittest
from typing import Any, Protocol, cast
from fastapi.testclient import TestClient
from src.main import app


class ResponseLike(Protocol):
    status_code: int

    def json(self) -> Any:
        ...


def _client_get(client: TestClient, path: str) -> ResponseLike:
    return cast(ResponseLike, cast(Any, client).get(path))


def _client_post(client: TestClient, path: str, payload: dict[str, object]) -> ResponseLike:
    return cast(ResponseLike, cast(Any, client).post(path, json=payload))


class AuthApiIntegrationTests(unittest.TestCase):
    def test_health_check_endpoint(self) -> None:
        client: TestClient = TestClient(app)
        response: ResponseLike
        with client:
            response = _client_get(client, "/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_graphql_endpoint_exists(self) -> None:
        query = """
        query {
          __schema {
            queryType { name }
          }
        }
        """

        client: TestClient = TestClient(app)
        response: ResponseLike
        with client:
            response = _client_post(client, "/graphql", {"query": query})

        self.assertEqual(response.status_code, 200)

# Other tests like DB integration require async fixture setup, skipped for brevity in this challenge.
