from typing import List
import rust_services as rs
from auth.ports.driving.auth_input_port import AuthInputPort
from person.ports.driving.person_input_port import PersonInputPort
from user_account.ports.driving.user_account_input_port import UserAccountInputPort


class AuthService(AuthInputPort):
    def __init__(self, person_service: PersonInputPort, user_account_service: UserAccountInputPort):
        self._person_service = person_service
        self._user_account_service = user_account_service

    async def login(self, identification_number: str, password: str) -> dict:
        person = await self._person_service.find_by_identification_number(identification_number)
        if not person:
            return {"success": False, "roles": []}

        user = await self._user_account_service.find_by_id(person.n_id_person)
        if not user or not user.c_salt:
            return {"success": False, "roles": []}

        enc_pwd_bytes = bytes.fromhex(user.c_hashed_password)
        is_valid = rs.ok_password(enc_pwd_bytes, user.c_salt, password)

        roles: List[str] = []
        if is_valid:
            roles = await self._person_service.get_person_roles(person.n_id_person)

        return {"success": is_valid, "roles": roles}
