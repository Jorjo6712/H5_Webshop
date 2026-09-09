from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Article, Order, OrderLine
from dtos.order_dto import CreateOrderDTO


class OrderService:
    def __init__(self, session: Session):
        self.session = session

    def create_order(
        self,
        dto: CreateOrderDTO,
        user_id: int | None = None,
        client_id: int | None = None
    ) -> Order:

        if not dto.items:
            raise ValueError(
                "Order must contain at least one item"
            )

        if user_id is None and client_id is None:
            raise ValueError(
                "Order must belong to a user or B2B client"
            )

        if user_id is not None and client_id is not None:
            raise ValueError(
                "Order cannot belong to both a user and B2B client"
            )

        order = Order(
            user_id=user_id,
            client_id=client_id,
            status="pending",
            total_amount=Decimal("0.00")
        )

        total_amount = Decimal("0.00")

        for item in dto.items:

            if item.quantity <= 0:
                raise ValueError(
                    "Quantity must be greater than zero"
                )

            article = self.session.scalar(
                select(Article).where(
                    Article.id == item.article_id
                )
            )

            if article is None:
                raise ValueError(
                    f"Article {item.article_id} does not exist"
                )

            if article.quantity_on_hand < item.quantity:
                raise ValueError(
                    f"Not enough stock for {article.name}"
                )

            article.quantity_on_hand -= item.quantity

            line_total = article.price * item.quantity
            total_amount += line_total

            order_line = OrderLine(
                article_id=article.id,
                quantity=item.quantity,
                unit_price=article.price
            )

            order.lines.append(order_line)

        order.total_amount = total_amount

        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)

        return order