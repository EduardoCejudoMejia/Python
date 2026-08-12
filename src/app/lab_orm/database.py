"""
database.py
-----------
Configuración de la conexión a la base de datos.

Por defecto usa un archivo SQLite local (lab.db), pero la misma función
sirve para crear un engine en memoria (":memory:"), muy útil en pruebas.

Para usar PostgreSQL o SQL Server solo cambiarías la URL, por ejemplo:
    PostgreSQL:  postgresql+psycopg2://user:password@localhost:5432/mi_db
    SQL Server:  mssql+pyodbc://user:password@servidor/mi_db?driver=ODBC+Driver+18+for+SQL+Server
El resto del código (modelos, CRUD) no cambia: esa es la ventaja de usar un ORM.
"""

from models import Base
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DB_URL = "sqlite:///lab.db"


def get_engine(db_url: str = DEFAULT_DB_URL, echo: bool = False):
    """Crea el engine de SQLAlchemy.

    echo=True imprime en consola cada sentencia SQL generada (útil para
    entender qué hace el ORM por debajo).
    """
    engine = create_engine(db_url, echo=echo, future=True)

    # SQLite no aplica claves foráneas por defecto; las activamos.
    if db_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def get_sessionmaker(engine) -> sessionmaker:
    return sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, future=True
    )


def init_db(engine) -> None:
    """Crea todas las tablas a partir de los modelos (Base.metadata).

    En un proyecto real esto normalmente NO se usa; en su lugar se aplican
    las migraciones de Alembic (ver carpeta alembic/). Aquí se deja como
    forma rápida de levantar el esquema para pruebas y demos.
    """
    Base.metadata.create_all(engine)


def new_session(db_url: str = DEFAULT_DB_URL, echo: bool = False) -> Session:
    """Atajo: crea engine + tablas + una sesión lista para usar."""
    engine = get_engine(db_url, echo=echo)
    init_db(engine)
    SessionLocal = get_sessionmaker(engine)
    return SessionLocal()
