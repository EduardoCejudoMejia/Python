from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/coches", tags=["Coches"])


@router.get("/", response_model=list[schemas.CocheOut])
def listar_coches(db: Session = Depends(get_db)):
    """Listado público del catálogo (no requiere login)."""
    return db.query(models.Coche).all()


@router.get("/{coche_id}", response_model=schemas.CocheOut)
def obtener_coche(coche_id: int, db: Session = Depends(get_db)):
    coche = db.query(models.Coche).filter(models.Coche.id == coche_id).first()
    if not coche:
        raise HTTPException(status_code=404, detail="Coche no encontrado")
    return coche


@router.post("/", response_model=schemas.CocheOut, status_code=status.HTTP_201_CREATED)
def crear_coche(
    coche: schemas.CocheCreate,
    db: Session = Depends(get_db),
    usuario: str = Depends(get_current_user),  # solo usuarios autenticados
):
    nuevo_coche = models.Coche(**coche.model_dump())
    db.add(nuevo_coche)
    db.commit()
    db.refresh(nuevo_coche)
    return nuevo_coche
