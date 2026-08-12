"""
main.py
-------
Demo end-to-end del laboratorio: crea un usuario, una orden con items,
y muestra cómo consultar los datos a través de las relaciones del ORM.

Ejecutar con:
    python main.py
"""

from decimal import Decimal

from crud import (
    create_order_with_items,
    create_user,
    list_orders_of_user,
    update_order_status,
)
from database import new_session


def main() -> None:
    # Sesión sobre un archivo SQLite local (lab.db). Se crea el esquema
    # automáticamente a partir de los modelos (equivalente rápido a
    # aplicar las migraciones de Alembic).
    session = new_session("sqlite:///lab.db", echo=False)

    # 1) Crear un usuario
    user = create_user(session, name="Lauraa Pérez", email="lauraa@example.com")
    print(f"Usuario creado: {user}")

    # 2) Crear una orden con varios items en una sola transacción
    order = create_order_with_items(
        session,
        user_id=user.id,
        items=[
            {
                "product_name": "Teclado mecánico",
                "quantity": 1,
                "unit_price": Decimal("59.90"),
            },
            {
                "product_name": "Mouse inalámbrico",
                "quantity": 2,
                "unit_price": Decimal("15.00"),
            },
        ],
    )
    print(f"Orden creada: {order} | total = {order.total}")

    # 3) Actualizar el estado de la orden
    update_order_status(session, order.id, "paid")

    # 4) Consultar las órdenes del usuario a través de la relación
    print(f"\nÓrdenes de {user.name}:")
    for o in list_orders_of_user(session, user.id):
        print(f"  - Orden #{o.id} | status={o.status} | total={o.total}")
        for item in o.items:
            print(
                f"      · {item.quantity}x {item.product_name} (${item.unit_price} c/u)"
            )

    session.close()


if __name__ == "__main__":
    main()
