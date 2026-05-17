from datetime import datetime
from typing import List
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from user_account.ports.driven.user_account_repository_port import UserAccountRepositoryPort
from user_account.domain.entities.user_account import UserAccount


Base = declarative_base()


class S02UserORM(Base):
    __tablename__ = "S02USER"

    nIdUser = Column("niduser", UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    cUsername = Column("cusername", String(20), nullable=False)
    cEmail = Column("cemail", String(100), nullable=False)
    cHashedPassword = Column("chashedpassword", String(256), nullable=False)
    cWallet = Column("cwallet", String(49), nullable=False)
    tLatestAccess = Column("tlatestaccess", DateTime)
    tCreatedAt = Column("createdat", DateTime, server_default=text("NOW()"))
    bIsActive = Column("bisactive", Boolean)


class PostgresUserAccountRepository(UserAccountRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_all(self) -> List[UserAccount]:
        stmt = select(S02UserORM).order_by(S02UserORM.tCreatedAt.desc())
        result = await self._session.execute(stmt)
        return [self._to_entity(row) for row in result.scalars().all()]

    def _to_entity(self, orm: S02UserORM) -> UserAccount:
        return UserAccount(
            n_id_user=str(orm.nIdUser) if orm.nIdUser else None,
            c_username=orm.cUsername,
            c_email=orm.cEmail,
            c_hashed_password=orm.cHashedPassword,
            c_wallet=orm.cWallet,
            t_latest_access=orm.tLatestAccess,
            created_at=orm.tCreatedAt,
            b_is_active=orm.bIsActive,
        )
