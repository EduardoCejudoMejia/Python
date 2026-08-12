"""
Dependencias de FastAPI reutilizables entre routers:
- get_db: entrega una sesión de base de datos y la cierra al terminar.
- get_current_user: exige y valida un JWT en el header Authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .database import SessionLocal
from .security import decodificar_access_token

# tokenUrl indica a /docs dónde se obtiene el token (botón "Authorize")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    error_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decodificar_access_token(token)
    if payload is None:
        raise error_credenciales

    username = payload.get("sub")
    if username is None:
        raise error_credenciales

    return username
