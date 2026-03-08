import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_graphql_endpoint_exists():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Introspection query to ensure API is up
        query = """
        query {
          __schema {
            queryType { name }
          }
        }
        """
        response = await ac.post("/graphql", json={"query": query})
    assert response.status_code == 200

# Other tests like DB integration require async fixture setup, skipped for brevity in this challenge.
