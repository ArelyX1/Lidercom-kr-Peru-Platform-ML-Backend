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

    @abstractmethod
    async def save_participant(self, n_id_person: str) -> None: ...

    @abstractmethod
    async def save_employee(self, n_id_person: str) -> None: ...

    @abstractmethod
    async def save_superior(self, n_id_person: str) -> None: ...

    @abstractmethod
    async def save_person_role(self, n_id_person: str, n_id_role: int) -> None: ...

    @abstractmethod
    async def find_role_names_by_person_id(self, n_id_person: str) -> List[str]: ...

    @abstractmethod
    async def find_permissions_by_person_id(self, n_id_person: str) -> List[dict]: ...

    @abstractmethod
    async def save_participant_program(self, n_id_participant: str, n_id_program: str) -> None: ...

    @abstractmethod
    async def find_programs_by_participant_id(self, n_id_person: str) -> List[dict]: ...

    @abstractmethod
    async def find_available_programs(self, n_id_person: str) -> List[dict]: ...
