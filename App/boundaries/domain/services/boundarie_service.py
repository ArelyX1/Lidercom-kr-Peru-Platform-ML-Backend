from typing import List
from boundaries.ports.driving.boundarie_input_port import BoundarieInputPort
from boundaries.ports.driven.boundarie_repository_port import BoundarieRepositoryPort
from boundaries.domain.entities.boundarie import Boundarie


class BoundarieService(BoundarieInputPort):
    def __init__(self, boundarie_repo: BoundarieRepositoryPort):
        self._boundarie_repo = boundarie_repo

    async def get_countries(self) -> List[Boundarie]:
        return await self._boundarie_repo.get_unique_countries()

    async def get_regions(self, country_gid: str) -> List[Boundarie]:
        return await self._boundarie_repo.get_regions_by_country(country_gid)

    async def get_provinces(self, region_gid: str) -> List[Boundarie]:
        return await self._boundarie_repo.get_provinces_by_region(region_gid)

    async def get_districts(self, province_gid: str) -> List[Boundarie]:
        return await self._boundarie_repo.get_districts_by_province(province_gid)
