"""
Owner: ArelyXl
Description: Implementa el adaptador de salida para el repositorio de usuarios usando SQLAlchemy ORM con PostgreSQL, con métodos para buscar y guardar usuarios (placeholder actual).
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.ports.driven.user_repository_port import UserRepositoryPort
from auth.domain.entities.user import User

class PostgresUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_email(self, email: str) -> Optional[User]:
        return None

    async def find_by_document(self, document_id: str) -> Optional[User]:
        return None

    async def save(self, user: User) -> User:
        return user
