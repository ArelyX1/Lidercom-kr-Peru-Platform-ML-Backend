import strawberry
from typing import List
from boundaries.domain.services.boundarie_service import BoundarieService
from boundaries.adapters.driven.postgres_boundarie_repository import PostgresBoundarieRepository
from db.config import AsyncSessionLocal


@strawberry.type
class Ubicacion:
    id: str
    nombre: str


@strawberry.type
class Query:
    @strawberry.field
    async def paises(self) -> List[Ubicacion]:
        async with AsyncSessionLocal() as session:
            repo = PostgresBoundarieRepository(session)
            service = BoundarieService(repo)
            return [Ubicacion(id=c.gid0, nombre=c.name0) for c in await service.get_countries()]

    @strawberry.field
    async def regiones(self, pais_id: str) -> List[Ubicacion]:
        async with AsyncSessionLocal() as session:
            repo = PostgresBoundarieRepository(session)
            service = BoundarieService(repo)
            return [Ubicacion(id=r.gid1, nombre=r.name1) for r in await service.get_regions(pais_id)]

    @strawberry.field
    async def provincias(self, region_id: str) -> List[Ubicacion]:
        async with AsyncSessionLocal() as session:
            repo = PostgresBoundarieRepository(session)
            service = BoundarieService(repo)
            return [Ubicacion(id=p.gid2, nombre=p.name2) for p in await service.get_provinces(region_id)]

    @strawberry.field
    async def distritos(self, provincia_id: str) -> List[Ubicacion]:
        async with AsyncSessionLocal() as session:
            repo = PostgresBoundarieRepository(session)
            service = BoundarieService(repo)
            return [Ubicacion(id=d.gid3, nombre=d.name3) for d in await service.get_districts(provincia_id)]
