from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from database.connection import get_session
from database.models import Article


articles_bp = Blueprint("articles", __name__)


@articles_bp.route("/api/articles", methods=["GET"])
@jwt_required()
def get_articles():
    with get_session() as session:
        articles = session.scalars(
            select(Article)
            .order_by(Article.id)
        ).all()

        return jsonify([
            {
                "id": article.id,
                "article_number": article.article_number,
                "name": article.name,
                "description": article.description,
                "price": str(article.price),
                "quantity_on_hand": article.quantity_on_hand,
                "created_at": article.created_at.isoformat()
            }
            for article in articles
        ]), 200


@articles_bp.route("/api/articles/<int:article_id>", methods=["GET"])
@jwt_required()
def get_article(article_id):
    with get_session() as session:
        article = session.scalar(
            select(Article)
            .where(Article.id == article_id)
        )

        if article is None:
            return jsonify({
                "error": "Article not found"
            }), 404

        return jsonify({
            "id": article.id,
            "article_number": article.article_number,
            "name": article.name,
            "description": article.description,
            "price": str(article.price),
            "quantity_on_hand": article.quantity_on_hand,
            "created_at": article.created_at.isoformat()
        }), 200