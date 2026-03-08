from dataclasses import dataclass
from typing import Optional
from .ports import UserReadModel, UserReadRepository

@dataclass
class GetUserByIdQuery:
    user_id: str

class GetUserByIdHandler:
    def __init__(self, read_repo: UserReadRepository):
        self._read_repo = read_repo

    async def handle(self, query: GetUserByIdQuery) -> Optional[UserReadModel]:
        return await self._read_repo.get_by_id(query.user_id)
