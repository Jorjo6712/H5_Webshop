from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class OrderLine(Base):
    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id")
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id")
    )

    quantity: Mapped[int]

    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2)
    )

    order = relationship(
        "Order",
        back_populates="lines"
    )