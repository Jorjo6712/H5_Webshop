from flask import Blueprint, request, render_template
from flask_jwt_extended import jwt_required

from database.connection import get_session

from services.article_service import ArticleService

web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET"])
@jwt_required()
def home():
    with get_session() as session:
        article_service = ArticleService(session)

        articles = article_service.get_article()

    return render_template("home.html", articles=articles)


