from abc import ABC, abstractmethod
from typing import List
from boundaries.domain.entities.boundarie import Boundarie


class BoundarieInputPort(ABC):
    @abstractmethod
    async def get_countries(self) -> List[Boundarie]: ...

    @abstractmethod
    async def get_regions(self, country_gid: str) -> List[Boundarie]: ...

    @abstractmethod
    async def get_provinces(self, region_gid: str) -> List[Boundarie]: ...

    @abstractmethod
    async def get_districts(self, province_gid: str) -> List[Boundarie]: ...
