from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from app.config import DB_DSN


class DBManagerBase:
    def __init__(self):
        self._engine: AsyncEngine = create_async_engine(DB_DSN, echo=True, future=True)

    @property
    def engine(self) -> AsyncEngine:
        return self._engine
