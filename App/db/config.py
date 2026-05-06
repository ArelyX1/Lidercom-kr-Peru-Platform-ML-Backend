"""
Owner: ArelyXl
Description: Configura la conexión asíncrona a PostgreSQL usando SQLAlchemy, definiendo el engine, la sesión asíncrona y la función para obtener la sesión de base de datos.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/dbname"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
