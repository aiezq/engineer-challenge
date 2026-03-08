from dataclasses import dataclass
from .ports import UserReadRepository

@dataclass
class ValidateResetTokenQuery:
    token: str

class ValidateResetTokenHandler:
    def __init__(self, read_repo: UserReadRepository):
        self._read_repo = read_repo

    async def handle(self, query: ValidateResetTokenQuery) -> bool:
        return await self._read_repo.is_reset_token_valid(query.token)
