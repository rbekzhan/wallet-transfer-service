import os
import logging

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.config import DB_DSN
from app.db_manager.tables import metadata


class Migration:
    def __init__(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        migrations_path = f"{current_path}/core"
        versions_path = f"{migrations_path}/versions"

        if os.path.exists(path=versions_path) is False:
            os.makedirs(name=versions_path)

        self.alembic_cfg = Config()
        self.alembic_cfg.set_main_option("script_location", migrations_path)
        self.alembic_cfg.set_main_option("sqlalchemy.url", DB_DSN)

        # logging.info(DB_DSN)

    def create_migrations(self) -> None:
        try:
            command.revision(self.alembic_cfg, autogenerate=True)
        except Exception as e:
            logging.error(e)

    def migrate(self):
        try:
            command.upgrade(self.alembic_cfg, "head")
        except Exception as e:
            logging.error(e)

    @staticmethod
    async def drop_all_tables():
        engine: AsyncEngine = create_async_engine(url=DB_DSN)
        async with engine.begin() as connection:
            await connection.run_sync(metadata.drop_all)

    @staticmethod
    async def create_all_tables():
        engine: AsyncEngine = create_async_engine(url=DB_DSN)
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
