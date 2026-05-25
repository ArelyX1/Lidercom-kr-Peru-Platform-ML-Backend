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

    @abstractmethod
    async def assign_role(self, n_id_person: str, n_id_role: int) -> None: ...

    @abstractmethod
    async def get_person_roles(self, n_id_person: str) -> List[str]: ...
