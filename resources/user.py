#import sqlite3

from flask_restful import Resource, reqparse
from models.user import UserModel


class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        "username",            
        type=str,
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument(
        "password",
        type=str,
        required=True,
        help="This field cannot be left blank!"
    )

    def post(self): 
        
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "User with that username allready exists!"}, 400

        user = UserModel(**data)
        user.save_to_db()    
        
        return{"message": "User created succsessfully."}, 201
    
# should try to put this delete method in the UserRegister class(rename it to User), by making the resource address:
# "/user/<string:username>" and then just not use the username for register method, just for delete method

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