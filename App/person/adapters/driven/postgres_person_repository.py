from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from person.ports.driven.person_repository_port import PersonRepositoryPort
from person.domain.entities.person import Person


Base = declarative_base()


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


class PostgresPersonRepository(PersonRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[Person]:
        stmt = select(S02PersonORM).order_by(S02PersonORM.tCreatedAt.desc())
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars().all()]

    async def find_by_identification_number(self, identification_number: str) -> Optional[Person]:
        stmt = select(S02PersonORM).where(S02PersonORM.cIdentificationNumber == identification_number)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_entity(orm) if orm else None

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
