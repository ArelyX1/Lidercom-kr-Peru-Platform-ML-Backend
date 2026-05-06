"""
Owner: ArelyXl
Description: Implementa el servicio de dominio AuthService que cumple con el puerto de entrada AuthInputPort, conteniendo la lógica de negocio para registro, login y consulta de ubicaciones geográficas para registro.
"""
from typing import List, Optional
from auth.ports.driving.auth_input_port import AuthInputPort
from auth.ports.driven.user_repository_port import UserRepositoryPort
from auth.ports.driven.boundarie_repository_port import BoundarieRepositoryPort
from auth.domain.entities.user import User
from auth.domain.entities.boundarie import Boundarie

class AuthService(AuthInputPort):
    def __init__(self, user_repo: UserRepositoryPort, boundarie_repo: BoundarieRepositoryPort):
        self._user_repo = user_repo
        self._boundarie_repo = boundarie_repo

    async def register_user(self, email: str, password: str, document_id: str, boundarie_id: str) -> dict:
        existing = await self._user_repo.find_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        
        user = User(
            document_id=document_id,
            email=email,
            password_hash=self._hash_password(password),
            boundarie_id=boundarie_id
        )
        saved = await self._user_repo.save(user)
        return {"id": saved.document_id, "email": saved.email}

    async def login(self, email: str, password: str) -> dict:
        user = await self._user_repo.find_by_email(email)
        if not user or not self._verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        return {"token": "jwt_token_here", "user_id": user.document_id}

    async def get_countries(self) -> List[Boundarie]:
        return await self._boundarie_repo.get_unique_countries()

    async def get_regions(self, country_gid: str) -> List[Boundarie]:
        return await self._boundarie_repo.get_regions_by_country(country_gid)

    async def get_provinces(self, region_gid: str) -> List[Boundarie]:
        return await self._boundarie_repo.get_provinces_by_region(region_gid)

    async def get_districts(self, province_gid: str) -> List[Boundarie]:
        return await self._boundarie_repo.get_districts_by_province(province_gid)

    def _hash_password(self, password: str) -> str:
        #tengo que meterlo al modulo de rust
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, hashed: str) -> bool:
        #Todo: mover esto al modulo de rust
        return self._hash_password(password) == hashed
