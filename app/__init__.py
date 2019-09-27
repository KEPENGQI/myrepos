from flask import Flask, Blueprint, make_response, jsonify
from flask_cors import CORS
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager
)

app = Flask(__name__)
bp = Blueprint("iconsult", __name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
jwt = JWTManager(app)

CORS(
    app,
    origins="*",
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Credentials"
    ],
    supports_credentials=True
)

from app.views import slot
from app.views import location
from app.views import slot_booking
from app.views import ACL
from app import errors
from app.views import SlotConfig
from app.views import archivedbooking
app.register_blueprint(bp, url_prefix='/iconsult')


@app.route('/')
def index():
    return jsonify({"message": "app working"})\



app.register_error_handler(405, lambda e: make_response(jsonify({

    "errors": [
        {
            "reason": "Method not allowed",
            "message": "Request method is not allowed by the server",
            "code": 405
        }
    ]
}), 405))

app.register_error_handler(500, lambda e: make_response(jsonify({
    "errors": [
        {
            "message": "Internal Server Error",
            "code": 500
        }
    ]
}), 500))
