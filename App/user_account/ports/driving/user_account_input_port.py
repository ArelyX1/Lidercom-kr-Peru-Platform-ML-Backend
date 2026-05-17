from abc import ABC, abstractmethod
from typing import List
from user_account.domain.entities.user_account import UserAccount


class UserAccountInputPort(ABC):
    @abstractmethod
    async def get_all(self) -> List[UserAccount]: ...
