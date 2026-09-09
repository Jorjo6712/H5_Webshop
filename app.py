import os

from flask import Flask, redirect
from flask_jwt_extended import JWTManager

from config import Config
from routes.auth import auth_bp
from routes.web import web_bp
from routes.orders import orders_bp
from routes.b2b import b2b_bp

print(os.getenv("DB_HOST"))

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return redirect("/login")

    @jwt.expired_token_loader
    def expired_callback(jwt_header, jwt_payload):
        return redirect("/login")

    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(b2b_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )