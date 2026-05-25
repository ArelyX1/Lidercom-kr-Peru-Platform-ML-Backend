import strawberry
from typing import List
from person.domain.services.person_service import PersonService
from person.adapters.driven.postgres_person_repository import PostgresPersonRepository
from person.domain.entities.person import Person as PersonEntity
from role.domain.services.role_service import RoleService
from role.adapters.driven.postgres_role_repository import PostgresRoleRepository
from db.config import AsyncSessionLocal


@strawberry.type
class Person:
    id: str
    name: str
    lastName: str
    id_identification_type: int
    identification_number: str
    birth_place_gadm: int | None = None
    residence_place_gadm: int | None = None
    created_at: str | None = None
    modified_at: str | None = None
    role: str


@strawberry.input
class CreatePersonInput:
    id_identification_type: int
    identification_number: str
    role_name: str


@strawberry.input
class UpdatePersonInput:
    identification_number: str
    name: str
    lastName: str
    birth_place_gadm: int
    residence_place_gadm: int


@strawberry.input
class AssignPersonRoleInput:
    identification_number: str
    role_name: str


@strawberry.type
class Query:
    @strawberry.field
    async def persons(self) -> List[Person]:
        async with AsyncSessionLocal() as session:
            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            items = await service.get_all()
            return [
                Person(
                    id=p.n_id_person,
                    name=p.c_name,
                    lastName=p.c_last_name,
                    id_identification_type=p.n_id_identification_type,
                    identification_number=p.c_identification_number,
                    birth_place_gadm=p.n_birth_place_gadm,
                    residence_place_gadm=p.n_residence_place_gadm,
                    created_at=str(p.t_created_at) if p.t_created_at else None,
                    modified_at=str(p.t_modified_at) if p.t_modified_at else None,
                    role=p.role_name,
                )
                for p in items
            ]

    @strawberry.field
    async def person(self, identification_number: str) -> Person | None:
        async with AsyncSessionLocal() as session:
            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            p = await service.find_by_identification_number(identification_number)
            if not p:
                return None
            return Person(
                id=p.n_id_person,
                name=p.c_name,
                lastName=p.c_last_name,
                id_identification_type=p.n_id_identification_type,
                identification_number=p.c_identification_number,
                birth_place_gadm=p.n_birth_place_gadm,
                residence_place_gadm=p.n_residence_place_gadm,
                created_at=str(p.t_created_at) if p.t_created_at else None,
                modified_at=str(p.t_modified_at) if p.t_modified_at else None,
                role=p.role_name or "",
            )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_person(self, input: CreatePersonInput) -> Person:
        async with AsyncSessionLocal() as session:
            role_repo = PostgresRoleRepository(session)
            role_service = RoleService(role_repo)
            role = await role_service.find_by_name(input.role_name)
            if not role:
                raise ValueError(f"Role '{input.role_name}' not found")

            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            entity = PersonEntity(
                c_name="",
                c_last_name="",
                n_id_identification_type=input.id_identification_type,
                c_identification_number=input.identification_number,
            )
            created = await service.create(entity)
            await service.assign_role(str(created.n_id_person), role.n_id_role)
            return Person(
                id=created.n_id_person,
                name=created.c_name,
                lastName=created.c_last_name,
                id_identification_type=created.n_id_identification_type,
                identification_number=created.c_identification_number,
                birth_place_gadm=created.n_birth_place_gadm,
                residence_place_gadm=created.n_residence_place_gadm,
                created_at=str(created.t_created_at) if created.t_created_at else None,
                modified_at=str(created.t_modified_at) if created.t_modified_at else None,
                role=created.role_name or "",
            )

    @strawberry.mutation
    async def update_person(self, input: UpdatePersonInput) -> Person:
        async with AsyncSessionLocal() as session:
            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            entity = PersonEntity(
                c_name=input.name.strip(),
                c_last_name=input.lastName.strip(),
                c_identification_number=input.identification_number,
                n_birth_place_gadm=input.birth_place_gadm,
                n_residence_place_gadm=input.residence_place_gadm,
            )
            updated = await service.update_by_identification_number(
                identification_number=input.identification_number,
                data=entity,
            )
            return Person(
                id=updated.n_id_person,
                name=updated.c_name,
                lastName=updated.c_last_name,
                id_identification_type=updated.n_id_identification_type,
                identification_number=updated.c_identification_number,
                birth_place_gadm=updated.n_birth_place_gadm,
                residence_place_gadm=updated.n_residence_place_gadm,
                created_at=str(updated.t_created_at) if updated.t_created_at else None,
                modified_at=str(updated.t_modified_at) if updated.t_modified_at else None,
                role=updated.role_name or "",
            )

    @strawberry.mutation
    async def assign_person_role(self, input: AssignPersonRoleInput) -> Person:
        async with AsyncSessionLocal() as session:
            role_repo = PostgresRoleRepository(session)
            role_service = RoleService(role_repo)
            role = await role_service.find_by_name(input.role_name)
            if not role:
                raise ValueError(f"Role '{input.role_name}' not found")

            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            person = await service.find_by_identification_number(input.identification_number)
            if not person:
                raise ValueError(f"Person with identification number '{input.identification_number}' not found")

            await service.assign_role(str(person.n_id_person), role.n_id_role)

            return Person(
                id=person.n_id_person,
                name=person.c_name,
                lastName=person.c_last_name,
                id_identification_type=person.n_id_identification_type,
                identification_number=person.c_identification_number,
                birth_place_gadm=person.n_birth_place_gadm,
                residence_place_gadm=person.n_residence_place_gadm,
                created_at=str(person.t_created_at) if person.t_created_at else None,
                modified_at=str(person.t_modified_at) if person.t_modified_at else None,
                role=role.c_name,
            )
