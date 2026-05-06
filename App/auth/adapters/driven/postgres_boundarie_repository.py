"""
Owner: ArelyXl
Description: Implementa el adaptador de salida para el repositorio de ubicaciones usando SQLAlchemy ORM con PostgreSQL, evitando SQL raw para prevenir inyección SQL. También contiene el modelo ORM S01BoundarieORM mapeado a la tabla S01BOUNDARIE.
"""
from typing import List
from sqlalchemy import select, distinct, and_
from sqlalchemy.ext.asyncio import AsyncSession
from auth.ports.driven.boundarie_repository_port import BoundarieRepositoryPort
from auth.domain.entities.boundarie import Boundarie

class PostgresBoundarieRepository(BoundarieRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_unique_countries(self) -> List[Boundarie]:
        stmt = (
            select(distinct(S01BoundarieORM.cGid0), S01BoundarieORM.cName0)
            .where(S01BoundarieORM.cGid0.isnot(None))
            .order_by(S01BoundarieORM.cName0)
        )
        result = await self._session.execute(stmt)
        return [Boundarie(gid0=row[0], name0=row[1]) for row in result.all()]

    async def get_regions_by_country(self, country_gid: str) -> List[Boundarie]:
        stmt = (
            select(distinct(S01BoundarieORM.cGid1), S01BoundarieORM.cName1)
            .where(
                and_(
                    S01BoundarieORM.cGid0 == country_gid,
                    S01BoundarieORM.cGid1.isnot(None)
                )
            )
            .order_by(S01BoundarieORM.cName1)
        )
        result = await self._session.execute(stmt)
        return [Boundarie(gid1=row[0], name1=row[1]) for row in result.all()]

    async def get_provinces_by_region(self, region_gid: str) -> List[Boundarie]:
        stmt = (
            select(distinct(S01BoundarieORM.cGid2), S01BoundarieORM.cName2)
            .where(
                and_(
                    S01BoundarieORM.cGid1 == region_gid,
                    S01BoundarieORM.cGid2.isnot(None)
                )
            )
            .order_by(S01BoundarieORM.cName2)
        )
        result = await self._session.execute(stmt)
        return [Boundarie(gid2=row[0], name2=row[1]) for row in result.all()]

    async def get_districts_by_province(self, province_gid: str) -> List[Boundarie]:
        stmt = (
            select(distinct(S01BoundarieORM.cGid3), S01BoundarieORM.cName3)
            .where(
                and_(
                    S01BoundarieORM.cGid2 == province_gid,
                    S01BoundarieORM.cGid3.isnot(None)
                )
            )
            .order_by(S01BoundarieORM.cName3)
        )
        result = await self._session.execute(stmt)
        return [Boundarie(gid3=row[0], name3=row[1]) for row in result.all()]


# ORM Model
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class S01BoundarieORM(Base):
    __tablename__ = "S01BOUNDARIE"
    
    nUidGadm = Column(Integer, primary_key=True)
    cGid0 = Column(String(5))
    cName0 = Column(String(100))
    cGid1 = Column(String(20))
    cName1 = Column(String(100))
    cGid2 = Column(String(20))
    cName2 = Column(String(100))
    cGid3 = Column(String(20))
    cName3 = Column(String(100))
