import strawberry
from auth.domain.services.auth_service import AuthService
from auth.adapters.driven.postgres_user_repository import PostgresUserRepository
from db.config import AsyncSessionLocal


@strawberry.type
class AuthPayload:
    token: str
    user_id: str


@strawberry.type
class RegisterResponse:
    id: str
    email: str


@strawberry.type
class Query:
    pass


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(self, email: str, password: str, document_id: str, boundarie_id: str) -> RegisterResponse:
        async with AsyncSessionLocal() as session:
            user_repo = PostgresUserRepository(session)
            service = AuthService(user_repo)
            result = await service.register_user(email, password, document_id, boundarie_id)
            return RegisterResponse(id=result["id"], email=result["email"])

    @strawberry.mutation
    async def login(self, email: str, password: str) -> AuthPayload:
        async with AsyncSessionLocal() as session:
            user_repo = PostgresUserRepository(session)
            service = AuthService(user_repo)
            result = await service.login(email, password)
            return AuthPayload(token=result["token"], user_id=result["user_id"])
