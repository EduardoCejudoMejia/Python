"""
crud.py
-------
Operaciones CRUD (Create, Read, Update, Delete) básicas usando el ORM.

Todas las funciones reciben una `Session` de SQLAlchemy ya abierta, para
que quien las use controle cuándo hacer commit/rollback (transacciones).
"""

from decimal import Decimal

from models import Order, OrderItem, User
from sqlalchemy import select
from sqlalchemy.orm import Session

# ---------- CREATE ----------


def create_user(session: Session, name: str, email: str) -> User:
    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    return user


def create_order(session: Session, user_id: int, status: str = "pending") -> Order:
    order = Order(user_id=user_id, status=status)
    session.add(order)
    session.commit()
    return order


def add_item_to_order(
    session: Session,
    order_id: int,
    product_name: str,
    quantity: int,
    unit_price: Decimal,
) -> OrderItem:
    item = OrderItem(
        order_id=order_id,
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
    )
    session.add(item)
    session.commit()
    return item


# ---------- READ ----------


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return session.execute(stmt).scalar_one_or_none()


def list_users(session: Session) -> list[User]:
    stmt = select(User).order_by(User.id)
    return list(session.execute(stmt).scalars())


def list_orders_of_user(session: Session, user_id: int) -> list[Order]:
    stmt = select(Order).where(Order.user_id == user_id).order_by(Order.id)
    return list(session.execute(stmt).scalars())


# ---------- UPDATE ----------


def update_order_status(session: Session, order_id: int, new_status: str) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise ValueError(f"No existe la orden con id={order_id}")
    order.status = new_status
    session.commit()
    return order


# ---------- DELETE ----------


def delete_user(session: Session, user_id: int) -> None:
    """Borra un usuario y, gracias al cascade definido en models.py,
    también sus órdenes e items asociados."""
    user = session.get(User, user_id)
    if user is None:
        return
    session.delete(user)
    session.commit()


# ---------- EJEMPLO DE TRANSACCIÓN ----------


def create_order_with_items(
    session: Session,
    user_id: int,
    items: list[dict],
) -> Order:
    """Crea una orden junto con todos sus items en una sola transacción.

    Si algo falla a mitad de camino, se hace rollback y no queda nada
    a medio guardar en la base de datos.
    """
    try:
        order = Order(user_id=user_id, status="pending")
        session.add(order)
        session.flush()  # asigna order.id sin cerrar la transacción

        for it in items:
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_name=it["product_name"],
                    quantity=it["quantity"],
                    unit_price=it["unit_price"],
                )
            )

        session.commit()
        return order
    except Exception:
        session.rollback()
        raise
