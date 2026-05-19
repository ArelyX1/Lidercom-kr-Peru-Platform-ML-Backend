from abc import ABC, abstractmethod
from typing import List, Optional
from person.domain.entities.person import Person


class PersonInputPort(ABC):
    @abstractmethod
    async def get_all(self) -> List[Person]: ...

    @abstractmethod
    async def find_by_identification_number(self, identification_number: str) -> Optional[Person]: ...

    @abstractmethod
    async def create(self, data: Person) -> Person: ...

    @abstractmethod
    async def update_by_identification_number(self, identification_number: str, data: Person) -> Person: ...
