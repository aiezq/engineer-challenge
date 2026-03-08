from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from src.api.graphql.schema import get_context, get_outbox_repo, schema
from src.config import get_settings
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.delivery.password_reset import build_password_reset_delivery
from src.infrastructure.observability.http_logging import add_http_logging_middleware
from src.infrastructure.observability.logger import log, setup_logging
from src.infrastructure.outbox.dispatcher import (
    OutboxDispatcher,
    OutboxDispatcherHandle,
    start_outbox_dispatcher,
    stop_outbox_dispatcher,
)


settings = get_settings()


def build_dispatcher() -> OutboxDispatcher:
    return OutboxDispatcher(
        session_factory=AsyncSessionLocal,
        outbox_repo_factory=get_outbox_repo,
        password_reset_delivery=build_password_reset_delivery(settings),
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    log.info("application_starting", app_env=settings.app_env)
    dispatcher_handle: Optional[OutboxDispatcherHandle] = await start_outbox_dispatcher(build_dispatcher())
    try:
        yield
    finally:
        await stop_outbox_dispatcher(dispatcher_handle)
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
