"""
Owner: ArelyXl
Description: Define la interfaz abstracta (puerto de salida) para el repositorio de usuarios, especificando los métodos que deben implementar los adaptadores de persistencia de usuarios.
"""
from abc import ABC, abstractmethod
from typing import Optional
from auth.domain.entities.user import User

class UserRepositoryPort(ABC):
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]: ...
    
    @abstractmethod
    async def find_by_document(self, document_id: str) -> Optional[User]: ...
    
    @abstractmethod
    async def save(self, user: User) -> User: ...
