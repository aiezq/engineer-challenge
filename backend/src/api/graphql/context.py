from typing import Optional, TypedDict
from fastapi import Request
from src.domain.exceptions import InvalidCredentialsError
from src.infrastructure.auth.token_service import JwtTokenService


class GraphQLContext(TypedDict):
    request: Request
    current_user_id: Optional[str]


def _extract_bearer_token(request: Request) -> Optional[str]:
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


async def build_context(request: Request, token_service: JwtTokenService) -> GraphQLContext:
    token = _extract_bearer_token(request)
    current_user_id = None
    if token:
        try:
            payload = token_service.decode_token(token)
        except InvalidCredentialsError:
            payload = {}

        current_user_id = payload.get("sub")

    return {
        "request": request,
        "current_user_id": current_user_id,
    }
