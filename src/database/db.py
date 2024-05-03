import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    """
    A class to manage database sessions for an async application.

    Attributes:
        _engine (AsyncEngine | None): The async SQLAlchemy engine.
        _session_maker (async_sessionmaker): The sessionmaker instance for creating sessions.

    Methods:
        session():
            A context manager that yields an AsyncSession. If an exception occurs, it rolls back the session.
            It also ensures that the session is closed after usage.
    """
    def __init__(self, url: str):
        """
        Initialize the DatabaseSessionManager with a database URL.

        Args:
            url (str): The database URL to connect to.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """
        A context manager that yields an AsyncSession.

        If an exception occurs, it rolls back the session. It also ensures that the session is closed after usage.

        Raises:
            Exception: If the session is not initialized.
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """
    A FastAPI dependency that provides a database session.

    This function is used as a dependency in FastAPI endpoints to get a database session.
    It uses the `sessionmanager` to create an async context with a database session.

    Yields:
        AsyncSession: The database session.
    """
    async with sessionmanager.session() as session:
        yield session

