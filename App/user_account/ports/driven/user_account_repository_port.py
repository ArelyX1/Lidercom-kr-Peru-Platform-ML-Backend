from abc import ABC, abstractmethod
from typing import List
from user_account.domain.entities.user_account import UserAccount


class UserAccountRepositoryPort(ABC):
    @abstractmethod
    async def find_all(self) -> List[UserAccount]: ...
