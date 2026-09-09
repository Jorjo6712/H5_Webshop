from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dtos.order_dto import CreateOrderDTO, OrderLineDTO
from database.connection import get_session
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
                "message": "Order created",
                "order_id": order.id,
                "status": order.status
            }), 201

    except (KeyError, TypeError, ValueError) as e:
        return jsonify({
            "error": str(e)
        }), 400