"""
models.py
---------
Modelos ORM con SQLAlchemy 2.0 (estilo declarativo con "Mapped").

Entidades:
    User       (1) ----- (N) Order
    Order      (1) ----- (N) OrderItem

Un usuario puede tener muchas órdenes.
Una orden puede tener muchos items (líneas de producto).
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Clase base declarativa. Todos los modelos heredan de aquí.

    Alembic usa Base.metadata para detectar los modelos y generar
    migraciones automáticas (--autogenerate).
    """

    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relación 1-a-N: un usuario tiene muchas órdenes.
    # cascade="all, delete-orphan" -> si se borra el user, se borran sus orders.
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} email={self.email!r}>"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Lado "muchos" de la relación con User
    user: Mapped["User"] = relationship(back_populates="orders")

    # Relación 1-a-N: una orden tiene muchos items
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    @property
    def total(self) -> Decimal:
        """Calcula el total sumando (precio * cantidad) de cada item."""
        return sum(
            (item.unit_price * item.quantity for item in self.items), Decimal("0")
        )

    def __repr__(self) -> str:
        return f"<Order id={self.id} user_id={self.user_id} status={self.status!r}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Lado "muchos" de la relación con Order
    order: Mapped["Order"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return (
            f"<OrderItem id={self.id} product={self.product_name!r} "
            f"qty={self.quantity} price={self.unit_price}>"
        )
