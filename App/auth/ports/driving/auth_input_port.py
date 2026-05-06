"""
Owner: ArelyXl
Description: Define la interfaz abstracta (puerto de entrada) para el módulo de autenticación, especificando los métodos que deben implementar los servicios de dominio para ser consumidos por adaptadores de entrada (GraphQL).
"""
from abc import ABC, abstractmethod
from typing import List
from auth.domain.entities.boundarie import Boundarie

class AuthInputPort(ABC):
    @abstractmethod
    async def register_user(self, email: str, password: str, document_id: str, boundarie_id: str) -> dict: ...
    
    @abstractmethod
    async def login(self, email: str, password: str) -> dict: ...
    
    @abstractmethod
    async def get_countries(self) -> List[Boundarie]: ...
    
    @abstractmethod
    async def get_regions(self, country_gid: str) -> List[Boundarie]: ...
    
    @abstractmethod
    async def get_provinces(self, region_gid: str) -> List[Boundarie]: ...
    
    @abstractmethod
    async def get_districts(self, province_gid: str) -> List[Boundarie]: ...
