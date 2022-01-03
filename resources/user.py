# import sqlite3
from flask_restful import Resource, reqparse
from models.user import UserModel
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)

# python convention: variables starting with _ are private variables
_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help="This field cannot be left blank!"
)
_user_parser.add_argument(
    "password", type=str, required=True, help="This field cannot be left blank!"
)


class UserRegister(Resource):
    def post(self):

        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "User with that username allready exists!"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created succsessfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}
        return user.json()

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User does not exist!"}
        user.delete_from_db()
        return {"message": "User deleted successfully."}


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        data = _user_parser.parse_args()

        # find user in database
        user = UserModel.find_by_username(data["username"])

        # check password
        if user and safe_str_cmp(data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        return {"message": "Invalid credentials"}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]  # jti is "JWT ID" a unique identifier for a JWT
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()

        # this was supposed to disable token refreshing for a token that has been blacklisted, but it doesn't work
        #        jti = get_jwt()["jti"]  # jti is "JWT ID" a unique identifier for a JWT
        #        if jti in BLACKLIST:
        #            return {"You have logged out. To continue please log in again"}
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
