import os

from flask import Flask, jsonify
from flask_restful import Api
from werkzeug.datastructures import _callback_property
from werkzeug.utils import header_property
from blacklist import BLACKLIST
from flask_jwt_extended import JWTManager

from resources.user import (
    TokenRefresh,
    User,
    UserRegister,
    UserLogin,
    TokenRefresh,
    UserLogout,
)
from resources.items import Item, ItemList
from resources.store import Store, StoreList
from datetime import timedelta


app = Flask(__name__)

app.config["DEBUG"] = True

# to make this work in heroku, .replace() changes postgres into postgresql,
# this is needed as these libraries are not updated in Heroku, whereas postres was changed to postresql
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace("://", "ql://", 1)  #, "sqlite:///data.db")
# another approach is to add a new configuration variable in Heroku->settings, I named it DATABASE_URL_SPECIAL
# and copied contents of DATABASE_URL configuration variable in it, than changed postgres to postgresql:
url = os.environ.get("DATABASE_URL").replace("postgres", "postgresql")
os.environ["DATABASE_URL_SPECIAL"] = url
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL_SPECIAL", "sqlite:///data.db"
)

# turns off the flask sqlalchemy modification tracker, because sqlalchemy has its own
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# To allow flask propagating exception even if debug is set to false on app
app.config["PROPAGATE_EXCEPTIONS"] = True
# by default blacklist is disabled so we have to enable it
# app.config["JWT_BLACKIST_ENABLED"] = True
# means we are enabling blacklist for both access and refresh tokens
# app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]

# authentication doesn't work if you don't set a secret_key / can't get a token
app.secret_key = "Zia_the_battle_dog"

# if you want app.secret_key and jwt_secret_key different than use:
# app.config["JWT_SECRET_KEY"] =...

# config JWT to expire within half an hour
app.config["JWT_EXPIRATION_DELTA"] = timedelta(seconds=30)

api = Api(app)


jwt = JWTManager(
    app
)  # does not automatically create and /auth endpoint, we do it ourselves


@jwt.additional_claims_loader
def add_claims_to_jwt(
    identity,
):  # remember identity is what we define when creating an access token (here identity=user_id)
    if (
        identity == 1
    ):  # here in real life we should read from database to get a list of administrators
        return {"is_admin": True}
    return {"is_admin": False}


# @jwt.token_in_blocklist_loader
# def check_if_token_in_blocklist(_decrypted_header, _decrypted_body): # was decrypted_token,
#    return _decrypted_body['sub'] in BLACKLIST # if exp ==True the token is blacklisted, no access _


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_headers, jwt_payload):
    return (
        jwt_payload["jti"] in BLACKLIST
    )  # jti means "JWT ID", a unique identifier for a JWT


@jwt.revoked_token_loader
def revoked_token_callback(jwt_headers, jwt_payload):
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


# the following 4 decorated functions are a means of configuring the api, to get personalized error messages with more detail
@jwt.expired_token_loader
def expired_token_callback(expired_token_header, expired_token_payload):
    return (
        jsonify({"description": "The token has expired.", "error": "token_expired"}),
        401,
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify({"description": "Invalid token format", "error": "invalid_token"}),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token",
                "error": "authorisation required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def not_fresh_token_callback(expired_token_header, expired_token_payload):
    return (
        jsonify(
            {"description": "The token is not fresh", "error": "authorisation_required"}
        ),
        401,
    )


api.add_resource(Store, "/store/<string:name>")
api.add_resource(Item, "/item/<string:name>")  # http://127.0.0.1:5000/item/itemsname
api.add_resource(ItemList, "/items")  # http:/127.0.0.1:5000/items
api.add_resource(UserRegister, "/register")  # http:/127.0.0.1:5000/register
api.add_resource(User, "/user/<int:user_id>")  # http:/127.0.0.1:5000/user/user_id
api.add_resource(StoreList, "/stores")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")

if __name__ == "__main__":
    from db import db

    db.init_app(app)

    if app.config["DEBUG"]:

        @app.before_first_request
        def create_tables():
            db.create_all()

    app.run(port=5000, debug=True)
