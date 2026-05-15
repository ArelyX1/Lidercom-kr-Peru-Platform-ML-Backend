"""
Owner: ArelyXl
Description: Contiene la definición de la entidad User como un dataclass, que representa el objeto de dominio de un usuario en el sistema con sus propiedades básicas para autenticación y registro.
"""
from dataclasses import dataclass
from typing import Optional
import rust_services as rs


@dataclass
class User:
    document_id: str
    email: str
    password_hash: str
    seed_hash: str
    phrase_hash: str
    crypto_pair: str
    salt: str
    boundarie_id: Optional[str] = None
    is_active: bool = True
