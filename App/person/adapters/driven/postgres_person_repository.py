from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, text, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from person.ports.driven.person_repository_port import PersonRepositoryPort
from person.domain.entities.person import Person
from db.base import Base
from role.adapters.driven.postgres_role_repository import S02PermissionORM, S02RolePermissionORM


class S02PersonORM(Base):
    __tablename__ = "S02PERSON"

    nIdPerson = Column("nidperson", UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    cName = Column("cname", String(100), nullable=False)
    cLastName = Column("clastname", String(100), nullable=False)
    nIdIdentificationType = Column("nididentificationtype", Integer, nullable=False)
    cIdentificationNumber = Column("cidentificationnumber", String(20), nullable=False)
    nBirthPlaceGadm = Column("nBirthPlaceGadm", Integer, quote=True)
    nResidencePlaceGadm = Column("nResidencePlaceGadm", Integer, quote=True)
    tCreatedAt = Column("tcreatedat", DateTime, server_default=text("NOW()"))
    tModifiedAt = Column("tmodifiedat", DateTime)


class S02PersonRoleORM(Base):
    __tablename__ = "S02PERSON_ROLE"

    nIdRole = Column("nidrole", Integer, ForeignKey("S02ROLE.nidrole"), primary_key=True)
    nIdPerson = Column("nidperson", UUID, ForeignKey("S02PERSON.nidperson"), primary_key=True)
    tCreatedAt = Column("tcreatedat", DateTime, server_default=text("NOW()"))


class S02ParticipantORM(Base):
    __tablename__ = "S02PARTICIPANT"

    nIdParticipant = Column("nidparticipant", UUID, ForeignKey("S02USER.niduser"), primary_key=True)
    bIsActive = Column("bisactive", Boolean, default=True)


class S02EmployeeORM(Base):
    __tablename__ = "S02EMPLOYEE"

    nIdEmployee = Column("nidemployee", UUID, ForeignKey("S02USER.niduser"), primary_key=True)
    bIsActive = Column("bisactive", Boolean, default=True)


class S02SuperiorORM(Base):
    __tablename__ = "S02SUPERIOR"

    nIdSuperior = Column("nidsuperior", UUID, ForeignKey("S02USER.niduser"), primary_key=True)
    bIsActive = Column("bisactive", Boolean, default=True)
    tCreatedAt = Column("tcreatedat", DateTime, server_default=text("NOW()"))


class S02ParticipantProgramORM(Base):
    __tablename__ = "S02PARTICIPANT_PROGRAM"

    nIdParticipant = Column("nidparticipant", UUID, ForeignKey("S02PARTICIPANT.nidparticipant"), primary_key=True)
    nIdProgram = Column("nidprogram", UUID, primary_key=True)
    bIsActive = Column("bisactive", Boolean, default=True)


class PostgresPersonRepository(PersonRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Person]:
        sql = text("""
            SELECT
                p.nidperson,
                p.cname,
                p.clastname,
                p.nididentificationtype,
                p.cidentificationnumber,
                p.tcreatedat,
                p.tmodifiedat,
                p."nBirthPlaceGadm",
                p."nResidencePlaceGadm",
                r.cname AS role_name
            FROM "S02PERSON" p
            LEFT JOIN "S02PERSON_ROLE" pr ON pr.nidperson = p.nidperson
            LEFT JOIN "S02ROLE" r ON r.nidrole = pr.nidrole
            ORDER BY p.tcreatedat DESC
        """)
        result = await self._session.execute(sql)
        rows = result.fetchall()
        return [
            Person(
                n_id_person=str(row[0]) if row[0] else None,
                c_name=row[1],
                c_last_name=row[2],
                n_id_identification_type=row[3],
                c_identification_number=row[4],
                t_created_at=row[5],
                t_modified_at=row[6],
                n_birth_place_gadm=row[7],
                n_residence_place_gadm=row[8],
                role_name=row[9] or "",
            )
            for row in rows
        ]

    async def find_by_identification_number(self, identification_number: str) -> Optional[Person]:
        sql = text("""
            SELECT
                p.nidperson,
                p.cname,
                p.clastname,
                p.nididentificationtype,
                p.cidentificationnumber,
                p.tcreatedat,
                p.tmodifiedat,
                p."nBirthPlaceGadm",
                p."nResidencePlaceGadm",
                r.cname AS role_name
            FROM "S02PERSON" p
            LEFT JOIN "S02PERSON_ROLE" pr ON pr.nidperson = p.nidperson
            LEFT JOIN "S02ROLE" r ON r.nidrole = pr.nidrole
            WHERE p.cidentificationnumber = :identification_number
        """)
        result = await self._session.execute(sql, {"identification_number": identification_number})
        row = result.fetchone()
        if not row:
            return None
        return Person(
            n_id_person=str(row[0]) if row[0] else None,
            c_name=row[1],
            c_last_name=row[2],
            n_id_identification_type=row[3],
            c_identification_number=row[4],
            t_created_at=row[5],
            t_modified_at=row[6],
            n_birth_place_gadm=row[7],
            n_residence_place_gadm=row[8],
            role_name=row[9] or "",
        )

    async def save(self, data: Person) -> Person:
        orm = S02PersonORM(
            cName=data.c_name,
            cLastName=data.c_last_name,
            nIdIdentificationType=data.n_id_identification_type,
            cIdentificationNumber=data.c_identification_number,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(orm)
        return self._to_entity(orm)

    async def save_participant(self, n_id_person: str) -> None:
        orm = S02ParticipantORM(nIdParticipant=n_id_person)
        self._session.add(orm)
        await self._session.flush()
        await self._session.commit()

    async def save_employee(self, n_id_person: str) -> None:
        orm = S02EmployeeORM(nIdEmployee=n_id_person)
        self._session.add(orm)
        await self._session.flush()
        await self._session.commit()

    async def save_superior(self, n_id_person: str) -> None:
        orm = S02SuperiorORM(nIdSuperior=n_id_person)
        self._session.add(orm)
        await self._session.flush()
        await self._session.commit()

    async def save_person_role(self, n_id_person: str, n_id_role: int) -> None:
        orm = S02PersonRoleORM(
            nIdPerson=n_id_person,
            nIdRole=n_id_role,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.commit()

    async def update(self, data: Person) -> Person:
        sql = text("""
            UPDATE "S02PERSON" SET
                cname = :cname,
                clastname = :clastname,
                "nBirthPlaceGadm" = :birth_place,
                "nResidencePlaceGadm" = :residence_place,
                tmodifiedat = :modified_at
            WHERE cidentificationnumber = :identification_number
            RETURNING *
        """)
        result = await self._session.execute(sql, {
            "cname": data.c_name,
            "clastname": data.c_last_name,
            "birth_place": data.n_birth_place_gadm,
            "residence_place": data.n_residence_place_gadm,
            "modified_at": datetime.now(),
            "identification_number": data.c_identification_number,
        })
        await self._session.commit()
        row = result.fetchone()
        if not row:
            raise ValueError(f"Person with identification number '{data.c_identification_number}' not found")
        return Person(
            n_id_person=str(row[0]) if row[0] else None,
            c_name=row[1],
            c_last_name=row[2],
            n_id_identification_type=row[3],
            c_identification_number=row[4],
            t_created_at=row[5],
            t_modified_at=row[6],
            n_birth_place_gadm=row[7],
            n_residence_place_gadm=row[8],
        )

    async def find_role_names_by_person_id(self, n_id_person: str) -> List[str]:
        sql = text("""
            SELECT r.cname
            FROM "S02PERSON_ROLE" pr
            JOIN "S02ROLE" r ON r.nidrole = pr.nidrole
            WHERE pr.nidperson = :person_id
        """)
        result = await self._session.execute(sql, {"person_id": n_id_person})
        return [row[0] for row in result.fetchall()]

    async def find_permissions_by_person_id(self, n_id_person: str) -> List[dict]:
        stmt = (
            select(S02PermissionORM)
            .join(S02RolePermissionORM, S02RolePermissionORM.nIdPermission == S02PermissionORM.nIdPermission)
            .join(S02PersonRoleORM, S02PersonRoleORM.nIdRole == S02RolePermissionORM.nIdRole)
            .where(S02PersonRoleORM.nIdPerson == n_id_person)
            .where(S02PermissionORM.bIsActive == True)
            .distinct()
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [
            {
                "name": p.cName,
                "code": p.cCode,
                "module": p.cModule,
                "description": p.cDescription,
            }
            for p in orms
        ]

    async def save_participant_program(self, n_id_participant: str, n_id_program: str) -> None:
        orm = S02ParticipantProgramORM(
            nIdParticipant=n_id_participant,
            nIdProgram=n_id_program,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.commit()

    async def find_programs_by_participant_id(self, n_id_person: str) -> List[dict]:
        sql = text("""
            SELECT
                p.nidprogram, p.cname, p.cdescription, p.cstatus,
                p.tstartdate, p.tendtime,
                w.nidworkshop, w.cdescription AS workshop_description,
                w.cstatus AS workshop_status, w.tdate
            FROM "S02PARTICIPANT_PROGRAM" pp
            JOIN "S01PROGRAM" p ON p.nidprogram = pp.nidprogram
            LEFT JOIN "S01WORKSHOP" w ON w.nidprogram = p.nidprogram AND w.bisactive = true
            WHERE pp.nidparticipant = :person_id AND p.bisactive = true
            ORDER BY p.tstartdate, w.tdate
        """)
        result = await self._session.execute(sql, {"person_id": n_id_person})
        rows = result.fetchall()
        programs: dict = {}
        for row in rows:
            pid = str(row[0])
            if pid not in programs:
                programs[pid] = {
                    "n_id_program": pid,
                    "c_name": row[1],
                    "c_description": row[2],
                    "c_status": row[3],
                    "t_start_date": str(row[4]) if row[4] else None,
                    "t_end_time": str(row[5]) if row[5] else None,
                    "workshops": [],
                }
            if row[6]:
                programs[pid]["workshops"].append({
                    "n_id_workshop": str(row[6]),
                    "c_description": row[7],
                    "c_status": row[8],
                    "t_date": str(row[9]) if row[9] else None,
                })
        return list(programs.values())

    async def find_available_programs(self, n_id_person: str) -> List[dict]:
        sql = text("""
            SELECT p.nidprogram, p.cname, p.cdescription, p.cstatus,
                   p.tstartdate, p.tendtime
            FROM "S01PROGRAM" p
            WHERE p.bisactive = true
              AND p.nidprogram NOT IN (
                SELECT pp.nidprogram FROM "S02PARTICIPANT_PROGRAM" pp
                WHERE pp.nidparticipant = :person_id
              )
            ORDER BY p.tstartdate
        """)
        result = await self._session.execute(sql, {"person_id": n_id_person})
        return [
            {
                "n_id_program": str(row[0]),
                "c_name": row[1],
                "c_description": row[2],
                "c_status": row[3],
                "t_start_date": str(row[4]) if row[4] else None,
                "t_end_time": str(row[5]) if row[5] else None,
            }
            for row in result.fetchall()
        ]

    def _to_entity(self, orm: S02PersonORM) -> Person:
        return Person(
            n_id_person=str(orm.nIdPerson) if orm.nIdPerson else None,
            c_name=orm.cName,
            c_last_name=orm.cLastName,
            n_id_identification_type=orm.nIdIdentificationType,
            c_identification_number=orm.cIdentificationNumber,
            n_birth_place_gadm=orm.nBirthPlaceGadm,
            n_residence_place_gadm=orm.nResidencePlaceGadm,
            t_created_at=orm.tCreatedAt,
            t_modified_at=orm.tModifiedAt,
        )
