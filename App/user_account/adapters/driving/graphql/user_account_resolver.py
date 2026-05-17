import strawberry
from typing import List
from user_account.domain.services.user_account_service import UserAccountService
from user_account.adapters.driven.postgres_user_account_repository import PostgresUserAccountRepository
from db.config import AsyncSessionLocal


@strawberry.type
class UserAccount:
    id: str
    username: str
    email: str
    wallet: str
    is_active: bool | None = None
    latest_access: str | None = None
    created_at: str | None = None


@strawberry.type
class Query:
    @strawberry.field
    async def user_accounts(self) -> List[UserAccount]:
        async with AsyncSessionLocal() as session:
            repo = PostgresUserAccountRepository(session)
            service = UserAccountService(repo)
            items = await service.get_all()
            return [
                UserAccount(
                    id=u.n_id_user,
                    username=u.c_username,
                    email=u.c_email,
                    wallet=u.c_wallet,
                    is_active=u.b_is_active,
                    latest_access=str(u.t_latest_access) if u.t_latest_access else None,
                    created_at=str(u.created_at) if u.created_at else None,
                )
                for u in items
            ]
