from typing import List, Optional
from person.ports.driving.person_input_port import PersonInputPort
from person.ports.driven.person_repository_port import PersonRepositoryPort
from person.domain.entities.person import Person


class PersonService(PersonInputPort):
    def __init__(self, repo: PersonRepositoryPort):
        self._repo = repo

    async def get_all(self) -> List[Person]:
        return await self._repo.find_all()

    async def find_by_identification_number(self, identification_number: str) -> Optional[Person]:
        return await self._repo.find_by_identification_number(identification_number)

    async def create(self, data: Person) -> Person:
        return await self._repo.save(data)

    async def update_by_identification_number(self, identification_number: str, data: Person) -> Person:
        existing = await self._repo.find_by_identification_number(identification_number)
        if not existing:
            raise ValueError(f"Person with identification number '{identification_number}' not found")
        return await self._repo.update(data)

    async def assign_role(self, n_id_person: str, n_id_role: int) -> None:
        await self._repo.save_person_role(n_id_person, n_id_role)
