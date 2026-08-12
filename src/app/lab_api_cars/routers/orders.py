from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=schemas.PedidoOut, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido: schemas.PedidoCreate,
    db: Session = Depends(get_db),
    usuario: str = Depends(get_current_user),
):
    """Crea un pedido, validando que el coche exista y que haya stock."""
    coche = db.query(models.Coche).filter(models.Coche.id == pedido.coche_id).first()
    if not coche:
        raise HTTPException(status_code=404, detail="El coche indicado no existe")
    if coche.stock < pedido.cantidad:
        raise HTTPException(
            status_code=400, detail="Stock insuficiente para este pedido"
        )

    coche.stock -= pedido.cantidad
    nuevo_pedido = models.Pedido(**pedido.model_dump())
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido


@router.get("/", response_model=list[schemas.PedidoOut])
def listar_pedidos(
    db: Session = Depends(get_db),
    usuario: str = Depends(get_current_user),
):
    return db.query(models.Pedido).all()


@router.get("/{pedido_id}", response_model=schemas.PedidoOut)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: str = Depends(get_current_user),
):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.put("/{pedido_id}", response_model=schemas.PedidoOut)
def actualizar_pedido(
    pedido_id: int,
    cambios: schemas.PedidoUpdate,
    db: Session = Depends(get_db),
    usuario: str = Depends(get_current_user),
):
    """Actualización parcial: solo se modifican los campos enviados."""
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    datos_nuevos = cambios.model_dump(exclude_unset=True)
    for campo, valor in datos_nuevos.items():
        setattr(pedido, campo, valor)

    db.commit()
    db.refresh(pedido)
    return pedido


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: str = Depends(get_current_user),
):
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    db.delete(pedido)
    db.commit()
    return None
