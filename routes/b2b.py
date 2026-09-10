from xmlrpc import client

from database.models import order
from flask import Blueprint, request, jsonify

from database.connection import get_session
from services.b2b_service import B2BService
from dtos.order_dto import CreateOrderDTO, OrderLineDTO
from services.order_service import OrderService

b2b_bp = Blueprint("b2b", __name__)


@b2b_bp.route("/api/b2b/orders", methods=["POST"])
def create_b2b_order():

    api_key = request.headers.get("X-API-Key")
    api_secret = request.headers.get("X-API-Secret")

    if not api_key or not api_secret:
        return jsonify({
            "error": "Missing B2B credentials"
        }), 401

    with get_session() as session:

        b2b_service = B2BService(session)

        client = b2b_service.authenticate(
            api_key,
            api_secret
        )

        if client is None:
            return jsonify({
                "error": "Invalid B2B credentials"
            }), 401

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
        except (KeyError, TypeError):
            return jsonify({
                "error": "Each item must contain article_id and quantity"
            }), 400

        order = OrderService(session).create_order(
            dto=dto,
            client_id=client.id
        )

        return jsonify({
            "message": "B2B order created successfully",
            "order_id": order.id,
            "company": client.company_name,
            "status": order.status,
            "total_amount": str(order.total_amount)
        }), 201 

@b2b_bp.route("/api/b2b/clients", methods=["POST"])
def create_b2b_client():

    data = request.get_json()

    company_name = data["company_name"]

    with get_session() as session:
        service = B2BService(session)

        client, api_secret = service.create_client(
            company_name
        )

        return jsonify({
            "company_name": client.company_name,
            "api_key": client.api_key,
            "api_secret": api_secret
        }), 201