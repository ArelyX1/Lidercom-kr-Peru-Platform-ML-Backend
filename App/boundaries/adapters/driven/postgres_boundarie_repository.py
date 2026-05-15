from typing import List
from sqlalchemy import select, distinct, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from boundaries.ports.driven.boundarie_repository_port import BoundarieRepositoryPort
from boundaries.domain.entities.boundarie import Boundarie


Base = declarative_base()


class S01BoundarieORM(Base):
    __tablename__ = "S01BOUNDARIE"

    nUidGadm = Column("nuidgadm", Integer, primary_key=True)
    cGid0 = Column("cgid0", String(5))
    cName0 = Column("cname0", String(100))
    cGid1 = Column("cgid1", String(20))
    cName1 = Column("cname1", String(100))
    cGid2 = Column("cgid2", String(20))
    cName2 = Column("cname2", String(100))
    cGid3 = Column("cgid3", String(20))
    cName3 = Column("cname3", String(100))


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
