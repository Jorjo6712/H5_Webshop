from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select

from database.connection import get_session
from database.models import Order
from dtos.order_dto import CreateOrderDTO, OrderLineDTO
from services.order_service import OrderService


orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/api/orders", methods=["POST"])
@jwt_required()
def create_order():
    data = request.get_json()

    if not data or "items" not in data:
        return jsonify({
            "error": "Order items are required"
        }), 400

    if not isinstance(data["items"], list) or not data["items"]:
        return jsonify({
            "error": "Order items must be a non-empty list"
        }), 400

    try:
        dto = CreateOrderDTO(
            items=[
                OrderLineDTO(
                    article_id=item["article_id"],
                    quantity=item["quantity"]
                )
                for item in data["items"]
            ]
        )

        user_id = int(get_jwt_identity())

        with get_session() as session:
            service = OrderService(session)

            order = service.create_order(
                dto=dto,
                user_id=user_id
            )

            return jsonify({
                "message": "Order created successfully",
                "order_id": order.id,
                "status": order.status,
                "total_amount": str(order.total_amount)
            }), 201

    except (KeyError, TypeError, ValueError) as e:
        return jsonify({
            "error": str(e)
        }), 400


@orders_bp.route("/api/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())

    with get_session() as session:
        orders = session.scalars(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.order_date.desc())
        ).all()

        return jsonify([
            {
                "id": order.id,
                "order_date": order.order_date.isoformat(),
                "status": order.status,
                "total_amount": str(order.total_amount)
            }
            for order in orders
        ]), 200

@orders_bp.route("/api/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())

    with get_session() as session:
        order = session.scalar(
            select(Order)
            .where(
                Order.id == order_id,
                Order.user_id == user_id
            )
        )

        if order is None:
            return jsonify({
                "error": "Order not found"
            }), 404

        return jsonify({
            "id": order.id,
            "order_date": order.order_date.isoformat(),
            "status": order.status,
            "total_amount": str(order.total_amount),
            "items": [
                {
                    "article_id": line.article_id,
                    "quantity": line.quantity,
                    "unit_price": str(line.unit_price)
                }
                for line in order.lines
            ]
        }), 200