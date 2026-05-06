"""
Owner: ArelyXl
Description: Implementa el adaptador de entrada GraphQL para el módulo de autenticación, definiendo los resolvers para queries de ubicaciones (paises, regiones, etc.) y mutations para registro y login, usando Strawberry GraphQL.
"""
import strawberry
from typing import List
from auth.ports.driving.auth_input_port import AuthInputPort
from auth.domain.services.auth_service import AuthService
from auth.adapters.driven.postgres_boundarie_repository import PostgresBoundarieRepository
from db.config import AsyncSessionLocal

@strawberry.type
class Ubicacion:
    id: str
    nombre: str

@strawberry.type
class AuthPayload:
    token: str
    user_id: str

@strawberry.type
class RegisterResponse:
    id: str
    email: str

async def get_auth_service() -> AuthInputPort:
    async with AsyncSessionLocal() as session:
        boundarie_repo = PostgresBoundarieRepository(session)
        from auth.adapters.driven.postgres_user_repository import PostgresUserRepository
        user_repo = PostgresUserRepository(session)
        return AuthService(user_repo, boundarie_repo)

@strawberry.type
class Query:
    @strawberry.field
    async def paises(self) -> List[Ubicacion]:
        service = await get_auth_service()
        return [Ubicacion(id=c.gid0, nombre=c.name0) for c in await service.get_countries()]

    @strawberry.field
    async def regiones(self, pais_id: str) -> List[Ubicacion]:
        service = await get_auth_service()
        return [Ubicacion(id=r.gid1, nombre=r.name1) for r in await service.get_regions(pais_id)]

    @strawberry.field
    async def provincias(self, region_id: str) -> List[Ubicacion]:
        service = await get_auth_service()
        return [Ubicacion(id=p.gid2, nombre=p.name2) for p in await service.get_provinces(region_id)]

    @strawberry.field
    async def distritos(self, provincia_id: str) -> List[Ubicacion]:
        service = await get_auth_service()
        return [Ubicacion(id=d.gid3, nombre=d.name3) for d in await service.get_districts(provincia_id)]

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(self, email: str, password: str, document_id: str, boundarie_id: str) -> RegisterResponse:
        service = await get_auth_service()
        result = await service.register_user(email, password, document_id, boundarie_id)
        return RegisterResponse(id=result["id"], email=result["email"])

    @strawberry.mutation
    async def login(self, email: str, password: str) -> AuthPayload:
        service = await get_auth_service()
        result = await service.login(email, password)
        return AuthPayload(token=result["token"], user_id=result["user_id"])
