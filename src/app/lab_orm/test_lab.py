"""
test_lab.py
-----------
Pruebas del CRUD usando una base de datos SQLite EN MEMORIA
("sqlite:///:memory:"). Cada test parte de una base de datos limpia,
lo cual es ideal para pruebas: rápido y sin dejar archivos en disco.

Ejecutar con:
    pytest -v
"""

from decimal import Decimal

import pytest
from crud import (
    create_order_with_items,
    create_user,
    delete_user,
    get_user_by_email,
    list_orders_of_user,
    update_order_status,
)
from database import get_engine, get_sessionmaker, init_db


@pytest.fixture()
def session():
    """Crea un engine SQLite en memoria, las tablas, y una sesión nueva
    para cada test."""
    engine = get_engine("sqlite:///:memory:")
    init_db(engine)
    SessionLocal = get_sessionmaker(engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_user(session):
    user = create_user(session, name="Luis Gómez", email="luis@example.com")

    assert user.id is not None
    assert get_user_by_email(session, "luis@example.com").name == "Luis Gómez"


def test_create_order_with_items_and_total(session):
    user = create_user(session, name="Marta Ruiz", email="marta@example.com")

    order = create_order_with_items(
        session,
        user_id=user.id,
        items=[
            {"product_name": "Libro", "quantity": 2, "unit_price": Decimal("10.00")},
            {"product_name": "Lámpara", "quantity": 1, "unit_price": Decimal("25.50")},
        ],
    )

    assert len(order.items) == 2
    assert order.total == Decimal("45.50")  # 2*10.00 + 1*25.50


def test_update_order_status(session):
    user = create_user(session, name="Pedro Díaz", email="pedro@example.com")
    order = create_order_with_items(
        session,
        user_id=user.id,
        items=[
            {"product_name": "Silla", "quantity": 1, "unit_price": Decimal("80.00")}
        ],
    )
    assert order.status == "pending"

    update_order_status(session, order.id, "paid")

    assert order.status == "paid"


def test_relationship_user_to_orders(session):
    user = create_user(session, name="Sofía León", email="sofia@example.com")
    create_order_with_items(
        session,
        user_id=user.id,
        items=[
            {"product_name": "Audífonos", "quantity": 1, "unit_price": Decimal("40.00")}
        ],
    )
    create_order_with_items(
        session,
        user_id=user.id,
        items=[
            {"product_name": "Cargador", "quantity": 3, "unit_price": Decimal("12.00")}
        ],
    )

    orders = list_orders_of_user(session, user.id)

    assert len(orders) == 2
    # También accesible directamente vía la relación user.orders
    assert len(user.orders) == 2


def test_delete_user_cascades_to_orders_and_items(session):
    user = create_user(session, name="Carlos Vega", email="carlos@example.com")
    order = create_order_with_items(
        session,
        user_id=user.id,
        items=[
            {"product_name": "Mochila", "quantity": 1, "unit_price": Decimal("55.00")}
        ],
    )
    order_id = order.id

    delete_user(session, user.id)

    # El usuario ya no existe
    assert get_user_by_email(session, "carlos@example.com") is None

    # Gracias al cascade="all, delete-orphan", la orden y sus items
    # también fueron eliminados.
    from models import Order

    assert session.get(Order, order_id) is None
