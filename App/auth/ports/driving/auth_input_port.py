from abc import ABC, abstractmethod


class AuthInputPort(ABC):
    @abstractmethod
    async def register_user(self, email: str, password: str, document_id: str, boundarie_id: str) -> dict: ...

    @abstractmethod
    async def login(self, email: str, password: str) -> dict: ...
