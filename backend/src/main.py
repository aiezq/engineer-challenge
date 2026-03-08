from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from src.api.graphql.schema import schema
from src.infrastructure.db.database import init_db

app = FastAPI(title="Orbitto Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/health")
def health_check():
    return {"status": "ok"}
