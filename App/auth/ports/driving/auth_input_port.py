from abc import ABC, abstractmethod


class AuthInputPort(ABC):
    @abstractmethod
    async def login(self, identification_number: str, password: str) -> dict: ...
