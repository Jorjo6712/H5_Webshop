from operator import add
from pickle import GET
import os

import bcrypt
from flask import Flask, request, redirect, render_template, session
from collections.abc import Mapping
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
    set_access_cookies,
    set_refresh_cookies
)
from werkzeug.security import check_password_hash

from bcrypt import hashpw
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import templates
from DTOs import RegisterUserDTO


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_SECURE"] = False
jwt = JWTManager(app)

# Connection configuration
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# SQLAlchemy bruger stadig psycopg som PostgreSQL driver
DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
session = Session(engine)

def unauthorized_callback(reason):
    return redirect("/login")
def expired_callback(jwt_header, jwt_payload):
    return redirect("/login")

jwt.unauthorized_loader(unauthorized_callback)
jwt.expired_token_loader(expired_callback)

# Base class for ORM classes
class Base(DeclarativeBase):
    pass


# ORM class der repræsenterer users tabellen
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password_hash: Mapped[str]

@app.route("/", methods=["GET", "POST"])
@jwt_required()
def home():

    if request.method == "POST":
        pass

    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():

        if request.method == "POST":
            userDto = RegisterUserDTO
            userDto.username = request.form["username"]
            userDto.password = request.form["password"]
            user = User()

            user.username = userDto.username
            user.password_hash = hashpw(userDto.password.encode(encoding="UTF-8"), bcrypt.gensalt()).decode(encoding="UTF-8")
            session.add(user)
            session.commit()

        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        print(DB_NAME)
        username = request.form["username"]
        password = request.form["password"]

        user = session.scalar(
            select(User).where(User.username == username)
        )

        if user and bcrypt.checkpw(password.encode(encoding="UTF-8"), user.password_hash.encode(encoding="UTF-8")):

            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            response = redirect("/")

            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            return response

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/refresh", methods=["POST"])
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)