from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from src.api.graphql.schema import get_context, schema
from src.config import get_settings
from src.infrastructure.db.database import init_db
from src.infrastructure.observability.http_logging import add_http_logging_middleware
from src.infrastructure.observability.logger import log, setup_logging


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    log.info("application_starting", app_env=settings.app_env)
    await init_db()
    yield
    log.info("application_stopping")


app = FastAPI(title="Orbitto Auth Service", lifespan=lifespan)
add_http_logging_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
def health_check():
    return {"status": "ok"}
