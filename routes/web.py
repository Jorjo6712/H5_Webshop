from flask import Blueprint, request, render_template, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity

from database.connection import get_session
from dtos.order_dto import CreateOrderDTO, OrderLineDTO

from services.article_service import ArticleService
from services.order_service import OrderService

web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET"])
@jwt_required()
def home():
    with get_session() as session:
        article_service = ArticleService(session)

        articles = article_service.get_article()

    return render_template("home.html", articles=articles)
