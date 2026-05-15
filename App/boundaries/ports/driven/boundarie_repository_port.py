from abc import ABC, abstractmethod
from typing import List
from boundaries.domain.entities.boundarie import Boundarie


class BoundarieRepositoryPort(ABC):
    @abstractmethod
    async def get_unique_countries(self) -> List[Boundarie]: ...

    @abstractmethod
    async def get_regions_by_country(self, country_gid: str) -> List[Boundarie]: ...

    @abstractmethod
    async def get_provinces_by_region(self, region_gid: str) -> List[Boundarie]: ...

    @abstractmethod
    async def get_districts_by_province(self, province_gid: str) -> List[Boundarie]: ...
