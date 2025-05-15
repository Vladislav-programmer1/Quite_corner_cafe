from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from .__all_models import *

__factory: async_sessionmaker | None = None


async def global_init(db_path: str = 'db/database.sqlite') -> None:
    """
    This func makes initialization of the database
    :param db_path: path to the database

    :return: None
    """
    global __factory
    if __factory:
        return
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.strip()}?check_same_thread=False")
    __factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with create_session():
        async with engine.begin() as connection:
            await connection.run_sync(SqlAlchemyBase.metadata.create_all)


def create_session() -> AsyncSession:
    """
    This func creates a new session.
    :return: Session
    """
    return __factory()
