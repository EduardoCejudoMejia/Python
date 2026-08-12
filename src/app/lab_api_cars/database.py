"""
Configuración de la base de datos.

En desarrollo se usa un archivo SQLite local (concesionario.db).
En los tests (ver tests/conftest.py) se sustituye por una base de datos
temporal distinta en cada ejecución, mediante override de la dependencia
`get_db`.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./concesionario.db")

# check_same_thread=False es necesario porque SQLite por defecto solo
# permite el uso desde el hilo que abrió la conexión, y uvicorn/pytest
# pueden usar varios hilos.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
