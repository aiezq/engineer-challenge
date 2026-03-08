from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional

@dataclass
class UserReadModel:
    id: str
    email: str
    is_active: bool
    created_at: str

class UserReadRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[UserReadModel]:
        pass

    @abstractmethod
    async def is_reset_token_valid(self, token: str) -> bool:
        pass
