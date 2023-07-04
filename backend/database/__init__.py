from time import sleep

from airports import db_insert_airports
from sqlalchemy import inspect

from .models import TABLES, Base
from .session import engine, is_ready

TABLE_NAMES = [table.__tablename__ for table in TABLES]


def init_db() -> None:
    """Initialze database."""
    while not is_ready():
        print("Wainting for database to be ready...")
        sleep(1)

    inspection = inspect(engine)
    tables = inspection.get_table_names()

    # initialize only when tables are non existing
    if len(set(TABLE_NAMES) - set(tables)) != 0:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        db_insert_airports()
