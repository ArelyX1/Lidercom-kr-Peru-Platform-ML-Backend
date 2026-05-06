"""
Owner: ArelyXl
Description: Contiene la definición de la entidad Boundarie como un dataclass, que representa una ubicación geográfica jerárquica (país, región, provincia, distrito) usada en el registro de usuarios.
"""
from dataclasses import dataclass

@dataclass
class Boundarie:
    gid0: str
    name0: str
    gid1: str | None = None
    name1: str | None = None
    gid2: str | None = None
    name2: str | None = None
    gid3: str | None = None
    name3: str | None = None
