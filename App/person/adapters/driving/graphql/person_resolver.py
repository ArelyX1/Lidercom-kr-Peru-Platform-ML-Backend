import strawberry
from typing import List
from person.domain.services.person_service import PersonService
from person.adapters.driven.postgres_person_repository import PostgresPersonRepository
from person.domain.entities.person import Person as PersonEntity
from role.domain.services.role_service import RoleService
from role.adapters.driven.postgres_role_repository import PostgresRoleRepository
from db.config import AsyncSessionLocal
from auth.adapters.driving.graphql.helpers import resolve_user_from_token


@strawberry.type
class Person:
    id: str
    name: str
    last_name: str
    id_identification_type: int
    identification_number: str
    birth_place_gadm: int | None = None
    residence_place_gadm: int | None = None
    created_at: str | None = None
    modified_at: str | None = None
    role: str


@strawberry.type
class WorkshopType:
    n_id_workshop: str
    c_description: str | None = None
    c_status: str | None = None
    t_date: str | None = None


@strawberry.type
class ProgramType:
    n_id_program: str
    c_name: str
    c_description: str | None = None
    c_status: str | None = None
    t_start_date: str | None = None
    t_end_time: str | None = None
    workshops: List[WorkshopType] | None = None


@strawberry.type
class AvailableProgramType:
    n_id_program: str
    c_name: str
    c_description: str | None = None
    c_status: str | None = None
    t_start_date: str | None = None
    t_end_time: str | None = None


@strawberry.input
class CreatePersonInput:
    id_identification_type: int
    identification_number: str
    role_name: str


@strawberry.input
class RegisterInput:
    identification_number: str
    name: str
    lastName: str
    birth_place_gadm: int
    residence_place_gadm: int


@strawberry.input
class UpdatePersonInput:
    identification_number: str
    name: str
    last_name: str
    birth_place_gadm: int
    residence_place_gadm: int


@strawberry.input
class AssignPersonRoleInput:
    identification_number: str
    role_name: str


@strawberry.input
class AssignParticipantProgramInput:
    identification_number: str
    program_id: str
    token: str


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
                    last_name=p.c_last_name,
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
                last_name=p.c_last_name,
                id_identification_type=p.n_id_identification_type,
                identification_number=p.c_identification_number,
                birth_place_gadm=p.n_birth_place_gadm,
                residence_place_gadm=p.n_residence_place_gadm,
                created_at=str(p.t_created_at) if p.t_created_at else None,
                modified_at=str(p.t_modified_at) if p.t_modified_at else None,
                role=p.role_name or "",
            )

    @strawberry.field
    async def participant_programs(self, identification_number: str, token: str) -> List[ProgramType]:
        await resolve_user_from_token(token)
        async with AsyncSessionLocal() as session:
            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            person = await service.find_by_identification_number(identification_number)
            if not person:
                raise ValueError(f"Person with identification number '{identification_number}' not found")
            data = await repo.find_programs_by_participant_id(str(person.n_id_person))
            return [
                ProgramType(
                    n_id_program=p["n_id_program"],
                    c_name=p["c_name"],
                    c_description=p["c_description"],
                    c_status=p["c_status"],
                    t_start_date=p["t_start_date"],
                    t_end_time=p["t_end_time"],
                    workshops=[WorkshopType(**w) for w in p["workshops"]] if p["workshops"] else [],
                )
                for p in data
            ]

    @strawberry.field
    async def available_programs(self, identification_number: str, token: str) -> List[AvailableProgramType]:
        await resolve_user_from_token(token)
        async with AsyncSessionLocal() as session:
            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            person = await service.find_by_identification_number(identification_number)
            if not person:
                raise ValueError(f"Person with identification number '{identification_number}' not found")
            data = await repo.find_available_programs(str(person.n_id_person))
            return [AvailableProgramType(**p) for p in data]

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
                last_name=created.c_last_name,
                id_identification_type=created.n_id_identification_type,
                identification_number=created.c_identification_number,
                birth_place_gadm=created.n_birth_place_gadm,
                residence_place_gadm=created.n_residence_place_gadm,
                created_at=str(created.t_created_at) if created.t_created_at else None,
                modified_at=str(created.t_modified_at) if created.t_modified_at else None,
                role=created.role_name or "",
            )

    @strawberry.mutation
    async def register(self, input: RegisterInput) -> Person:
        async with AsyncSessionLocal() as session:
            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            existing = await service.find_by_identification_number(input.identification_number)
            if not existing:
                raise ValueError(f"Person with identification number '{input.identification_number}' not found")

            role_name = existing.role_name.lower()
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
                last_name=updated.c_last_name,
                id_identification_type=updated.n_id_identification_type,
                identification_number=updated.c_identification_number,
                birth_place_gadm=updated.n_birth_place_gadm,
                residence_place_gadm=updated.n_residence_place_gadm,
                created_at=str(updated.t_created_at) if updated.t_created_at else None,
                modified_at=str(updated.t_modified_at) if updated.t_modified_at else None,
                role=role_name,
            )

    @strawberry.mutation
    async def update_person(self, input: UpdatePersonInput) -> Person:
        async with AsyncSessionLocal() as session:
            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            existing = await service.find_by_identification_number(input.identification_number)
            if not existing:
                raise ValueError(f"Person with identification number '{input.identification_number}' not found")

            role_name = existing.role_name.lower()
            entity = PersonEntity(
                c_name=input.name.strip(),
                c_last_name=input.last_name.strip(),
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
                last_name=updated.c_last_name,
                id_identification_type=updated.n_id_identification_type,
                identification_number=updated.c_identification_number,
                birth_place_gadm=updated.n_birth_place_gadm,
                residence_place_gadm=updated.n_residence_place_gadm,
                created_at=str(updated.t_created_at) if updated.t_created_at else None,
                modified_at=str(updated.t_modified_at) if updated.t_modified_at else None,
                role=role_name,
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
                last_name=person.c_last_name,
                id_identification_type=person.n_id_identification_type,
                identification_number=person.c_identification_number,
                birth_place_gadm=person.n_birth_place_gadm,
                residence_place_gadm=person.n_residence_place_gadm,
                created_at=str(person.t_created_at) if person.t_created_at else None,
                modified_at=str(person.t_modified_at) if person.t_modified_at else None,
                role=role.c_name,
            )

    @strawberry.mutation
    async def assign_participant_program(self, input: AssignParticipantProgramInput) -> str:
        await resolve_user_from_token(input.token)
        async with AsyncSessionLocal() as session:
            repo = PostgresPersonRepository(session)
            service = PersonService(repo)
            person = await service.find_by_identification_number(input.identification_number)
            if not person:
                raise ValueError(f"Person with identification number '{input.identification_number}' not found")
            await repo.save_participant_program(str(person.n_id_person), input.program_id)
            return "OK"
