from typing import List
import strawberry
from auth.domain.services.auth_service import AuthService
from person.domain.services.person_service import PersonService
from person.adapters.driven.postgres_person_repository import PostgresPersonRepository
from user_account.domain.services.user_account_service import UserAccountService
from user_account.adapters.driven.postgres_user_account_repository import PostgresUserAccountRepository
from db.config import AsyncSessionLocal


@strawberry.type
class LoginPayload:
    success: bool
    roles: List[str]


@strawberry.type
class Query:
    pass


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def login(self, identification_number: str, password: str) -> LoginPayload:
        async with AsyncSessionLocal() as session:
            person_repo = PostgresPersonRepository(session)
            user_account_repo = PostgresUserAccountRepository(session)
            service = AuthService(PersonService(person_repo), UserAccountService(user_account_repo))
            result = await service.login(identification_number, password)
            return LoginPayload(success=result["success"], roles=result.get("roles", []))
