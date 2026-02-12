import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL, create_engine
from functools import cache

load_dotenv()


# MODIFIED: load sqlalchemy url from environment
# references:
# - https://github.com/sqlalchemy/alembic/discussions/1043#discussioncomment-12383677
# - https://github.com/sqlalchemy/alembic/discussions/1043#discussioncomment-12385267
def sqlalchemy_url_from_env() -> URL:
    db_driver = os.environ.get("DB_DRIVER", "sqlite")
    if db_driver == "sqlite":
        db_fname = os.environ.get("DB_FNAME", "default.db")
        return URL.create(drivername=db_driver, database=db_fname)
    else:
        db_user = os.environ.get("DB_USER", "alvin")
        db_password = os.environ.get("DB_PASSWORD", "password")
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = int(os.environ.get("DB_PORT", "5432"))
        db_name = os.environ.get("DB_NAME", "finance")
        return URL.create(
            drivername=db_driver,
            username=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name,
        )


@cache
def get_engine():
    return create_engine(sqlalchemy_url_from_env())