from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserAccount:
    n_id_user: Optional[str] = None
    c_username: str = ""
    c_email: str = ""
    c_hashed_password: str = ""
    c_wallet: str = ""
    t_latest_access: Optional[datetime] = None
    created_at: Optional[datetime] = None
    b_is_active: Optional[bool] = True
