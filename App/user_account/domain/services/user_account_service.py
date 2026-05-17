from typing import List
from user_account.ports.driving.user_account_input_port import UserAccountInputPort
from user_account.ports.driven.user_account_repository_port import UserAccountRepositoryPort
from user_account.domain.entities.user_account import UserAccount


class UserAccountService(UserAccountInputPort):
    def __init__(self, repo: UserAccountRepositoryPort):
        self._repo = repo

    async def get_all(self) -> List[UserAccount]:
        return await self._repo.find_all()
