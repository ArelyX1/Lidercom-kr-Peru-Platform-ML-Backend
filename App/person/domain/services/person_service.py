from typing import List
from person.ports.driving.person_input_port import PersonInputPort
from person.ports.driven.person_repository_port import PersonRepositoryPort
from person.domain.entities.person import Person


class PersonService(PersonInputPort):
    def __init__(self, repo: PersonRepositoryPort):
        self._repo = repo

    async def get_all(self) -> List[Person]:
        return await self._repo.find_all()

    async def create(self, data: Person) -> Person:
        return await self._repo.save(data)

    async def update_by_identification_number(self, identification_number: str, data: Person) -> Person:
        existing = await self._repo.find_by_identification_number(identification_number)
        if not existing:
            raise ValueError(f"Person with identification number '{identification_number}' not found")
        return await self._repo.update(data)
