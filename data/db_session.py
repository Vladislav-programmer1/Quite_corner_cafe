import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import Session

__factory: orm.sessionmaker | None = None
SqlAlchemyBase: orm.DeclarativeBase = orm.declarative_base()


def global_init(db_path: str = 'db/database.sqlite') -> None:
    """
    This func makes initialization of the database
    :param db_path: path to the database

    :return: None
    """
    global __factory
    if __factory:
        return
    engine = sa.create_engine(f"sqlite:///{db_path.strip()}&check_same_thread=False")
    __factory = orm.sessionmaker(bind=engine)
    from . import __all_models
    if __all_models:
        pass
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    """
    This func creates a new session.
    :return: Session
    """
    return __factory()
