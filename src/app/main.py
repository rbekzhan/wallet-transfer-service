import uvicorn

from app.db_manager.migrations.auto_migrate import Migration
from app.route import app


def create_migrations():
    migration = Migration()
    migration.create_migrations()


def migrate():
    migration = Migration()
    migration.migrate()



def start():
    uvicorn.run(app, host="0.0.0.0", port=8080)
