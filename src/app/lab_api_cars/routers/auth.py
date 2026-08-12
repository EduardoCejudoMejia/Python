from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas import Token
from ..security import autenticar_usuario, crear_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login básico: recibe username/password como form-data (estándar
    OAuth2) y devuelve un JWT si son correctos.

    Usuario de prueba: admin / admin123
    """
    usuario = autenticar_usuario(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = crear_access_token(data={"sub": usuario["username"]})
    return Token(access_token=access_token)
