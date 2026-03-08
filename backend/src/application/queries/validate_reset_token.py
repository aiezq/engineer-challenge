from dataclasses import dataclass
from src.application.ports import TokenService
from .ports import UserReadRepository

@dataclass
class ValidateResetTokenQuery:
    token: str

class ValidateResetTokenHandler:
    def __init__(self, read_repo: UserReadRepository, token_service: TokenService):
        self._read_repo = read_repo
        self._token_service = token_service

    async def handle(self, query: ValidateResetTokenQuery) -> bool:
        token_hash = self._token_service.hash_reset_token(query.token)
        return await self._read_repo.is_reset_token_valid(token_hash)
