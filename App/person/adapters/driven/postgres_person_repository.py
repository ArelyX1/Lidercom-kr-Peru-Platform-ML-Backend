from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, text, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from person.ports.driven.person_repository_port import PersonRepositoryPort
from person.domain.entities.person import Person
from db.base import Base


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
