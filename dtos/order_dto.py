from dataclasses import dataclass


@dataclass
class OrderLineDTO:
    article_id: int
    quantity: int


@dataclass
class CreateOrderDTO:
    items: list[OrderLineDTO]