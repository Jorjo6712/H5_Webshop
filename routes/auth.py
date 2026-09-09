from flask import Blueprint, request, redirect, render_template
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    get_jwt_identity
)

from dtos.user_dto import UserDTO
from database.connection import get_session
from services.auth_service import AuthService


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        dto = UserDTO(
            username=request.form["username"],
            password=request.form["password"]
        )

        with get_session() as session:
            auth_service = AuthService(session)

            auth_service.register_user(dto)

        return redirect("/login")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        with get_session() as session:
            auth_service = AuthService(session)

            user = auth_service.authenticate_user(
                username,
                password
            )

        if user is None:
            return "Invalid username or password", 401

        access_token = create_access_token(
            identity=str(user.id)
        )

        refresh_token = create_refresh_token(
            identity=str(user.id)
        )

        response = redirect("/")

        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response

    return render_template("login.html")

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    current_user_id = get_jwt_identity()

    access_token = create_access_token(
        identity=current_user_id
    )

    response = {
        "message": "Access token refreshed"
    }

    set_access_cookies(response, access_token)

    return response