from typing import Optional
from auth.ports.driving.auth_input_port import AuthInputPort
from auth.ports.driven.user_repository_port import UserRepositoryPort
from auth.domain.entities.user import User


class AuthService(AuthInputPort):
    def __init__(self, user_repo: UserRepositoryPort):
        self._user_repo = user_repo

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

    def _hash_password(self, password: str) -> str:
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, hashed: str) -> bool:
        return self._hash_password(password) == hashed
