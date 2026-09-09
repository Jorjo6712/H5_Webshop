from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required


web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET"])
@jwt_required()
def home():
    return render_template("home.html")