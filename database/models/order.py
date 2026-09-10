from datetime import datetime
from decimal import Decimal
from xmlrpc.client import DateTime

from sqlalchemy import ForeignKey, Numeric, String, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("b2b_clients.id"),
        nullable=True
    )

    order_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending"
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    lines = relationship(
        "OrderLine",
        back_populates="order",
        cascade="all, delete-orphan"
    )