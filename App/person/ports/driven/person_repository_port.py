from abc import ABC, abstractmethod
from typing import List, Optional
from person.domain.entities.person import Person


class PersonRepositoryPort(ABC):
    @abstractmethod
    async def find_all(self) -> List[Person]: ...

    @abstractmethod
    async def find_by_identification_number(self, identification_number: str) -> Optional[Person]: ...

    @abstractmethod
    async def save(self, data: Person) -> Person: ...

    @abstractmethod
    async def update(self, data: Person) -> Person: ...
