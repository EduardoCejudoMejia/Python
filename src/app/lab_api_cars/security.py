"""
Utilidades de autenticación: hashing de contraseñas y creación/lectura
de tokens JWT.

Para mantener el laboratorio simple, el "usuario" vive en un diccionario
en memoria en lugar de una tabla de base de datos. En un proyecto real,
SECRET_KEY debe venir de una variable de entorno y los usuarios de la DB.
"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "clave-secreta-de-laboratorio-no-usar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Usuario único de ejemplo: admin / admin123
USUARIOS_DEMO = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
    }
}


def verificar_password(password_plano: str, password_hash: str) -> bool:
    return pwd_context.verify(password_plano, password_hash)


def autenticar_usuario(username: str, password: str) -> dict | None:
    usuario = USUARIOS_DEMO.get(username)
    if not usuario or not verificar_password(password, usuario["hashed_password"]):
        return None
    return usuario


def crear_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    datos_token = data.copy()
    expiracion = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    datos_token.update({"exp": expiracion})
    return jwt.encode(datos_token, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
