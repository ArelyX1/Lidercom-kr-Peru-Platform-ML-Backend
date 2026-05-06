"""
Owner: ArelyXl
Description: Define la interfaz abstracta (puerto de salida) para el repositorio de ubicaciones geográficas (Boundarie), especificando métodos para consultar países, regiones, provincias y distritos.
"""
from abc import ABC, abstractmethod
from typing import List
from auth.domain.entities.boundarie import Boundarie

class BoundarieRepositoryPort(ABC):
    @abstractmethod
    async def get_unique_countries(self) -> List[Boundarie]: ...
    
    @abstractmethod
    async def get_regions_by_country(self, country_gid: str) -> List[Boundarie]: ...
    
    @abstractmethod
    async def get_provinces_by_region(self, region_gid: str) -> List[Boundarie]: ...
    
    @abstractmethod
    async def get_districts_by_province(self, province_gid: str) -> List[Boundarie]: ...
