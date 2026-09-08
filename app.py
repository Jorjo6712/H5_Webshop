from operator import add
from pickle import GET
import os

import bcrypt
from flask import Flask, request, redirect, render_template
from collections.abc import Mapping
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from werkzeug.security import check_password_hash

from bcrypt import hashpw
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import templates
from DTOs import RegisterUserDTO


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
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


# Base class for ORM classes
class Base(DeclarativeBase):
    pass


# ORM class der repræsenterer users tabellen
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password_hash: Mapped[str]


# ORM class der repræsenterer articles tabellen
class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_number: Mapped[str]
    name: Mapped[str]
    price: Mapped[float]
    quantity_on_hand: Mapped[int]


# Standard route
@app.route("/")
def home():
    return """
        <h1>Server Side Programming</h1>
        <p><a href="/login">Login</a></p>
        <p><a href="/register">Register</a></p>
        <p><a href="/inventory">Inventory</a></p>
    """

@app.route("/register", methods=["GET", "POST"])
def register():

        if request.method == "POST":
            userDto = RegisterUserDTO
            userDto.username = request.form["username"]
            userDto.password = request.form["password"]
            user = User()

            with Session(engine) as session:
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

        with Session(engine) as session:

            user = session.scalar(
                select(User).where(User.username == username)
            )

        if user and bcrypt.checkpw(password.encode(encoding="UTF-8"), user.password_hash.encode(encoding="UTF-8")):

            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/inventory")
@jwt_required()
def inventory():

    with Session(engine) as session:

        articles = session.scalars(
            select(Article).order_by(Article.article_number)
        ).all()

    html = """
        <h1>Inventory</h1>

        <table border="1">
            <tr>
                <th>Article</th>
                <th>Name</th>
                <th>Price</th>
                <th>Stock</th>
            </tr>
    """

    # article er nu et Article objekt og ikke en tuple
    for article in articles:
        html += f"""
            <tr>
                <td>{article.article_number}</td>
                <td>{article.name}</td>
                <td>{article.price}</td>
                <td>{article.quantity_on_hand}</td>
            </tr>
        """

    html += "</table>"

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)