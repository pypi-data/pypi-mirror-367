from enum import Enum

class DBPackages(str, Enum):
    SQLMODEL = "sqlmodel"
    SQLALCHEMY = "sqlalchemy"
    ALEMBIC = "alembic"
