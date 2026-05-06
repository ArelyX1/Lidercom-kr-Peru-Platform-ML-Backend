"""
Owner: ArelyXl
Description: Contiene la definición de la entidad User como un dataclass, que representa el objeto de dominio de un usuario en el sistema con sus propiedades básicas para autenticación y registro.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    document_id: str
    email: str
    password_hash: str
    seed_hash: str
    salt: str
    phrase_hash: str
    boundarie_id: Optional[str] = None
    is_active: bool = True
