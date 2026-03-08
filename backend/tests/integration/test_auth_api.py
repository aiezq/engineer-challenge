import unittest
from fastapi.testclient import TestClient
from src.main import app


class AuthApiIntegrationTests(unittest.TestCase):
    def test_health_check_endpoint(self) -> None:
        with TestClient(app) as client:
            response = client.get("/health")

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

        with TestClient(app) as client:
            response = client.post("/graphql", json={"query": query})

        self.assertEqual(response.status_code, 200)

# Other tests like DB integration require async fixture setup, skipped for brevity in this challenge.
