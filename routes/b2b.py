from flask import Blueprint, request, jsonify

from database.connection import get_session
from services.b2b_service import B2BService
from dtos.order_dto import CreateOrderDTO, OrderLineDTO

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

        dto = CreateOrderDTO(
            items=[
                OrderLineDTO(
                    article_id=item["article_id"],
                    quantity=item["quantity"]
                )
                for item in data["items"]
            ]
        )

        # OrderService will be implemented next.
        # order = OrderService(session).create_order(
        #     client.id,
        #     dto
        # )

        return jsonify({
            "message": "B2B authentication successful",
            "company": client.company_name
        }), 200

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