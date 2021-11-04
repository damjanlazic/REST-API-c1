import os

from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserDelete, UserRegister
from resources.items import Item, ItemList
from resources.store import Store, StoreList
from datetime import timedelta
#from db import db


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data.db")
# turns off the flask sqlalchemy modification tracker, because sqlalchemy has its own
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
# To allow flask propagating exception even if debug is set to false on app
app.config['PROPAGATE_EXCEPTIONS'] = True
# authentication doesn't work if you don't set a secret_key / can't get a token
app.secret_key = "Zia_the_battle_dog"
# config JWT to expire within half an hour
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)

api = Api(app)

# this automatically creates all the required tables in the data.db file if they don't exist already
# it happens immediately before the first request is made,
# @app.before_first_request
# def create_tables():
#    db.create_all()


jwt = JWT(app, authenticate, identity) # /auth

api.add_resource(Store, "/store/<string:name>")
api.add_resource(Item, "/item/<string:name>") #http://127.0.0.1:5000/item/itemsname
api.add_resource(ItemList, "/items") # http:/127.0.0.1:5000/items
api.add_resource(UserRegister, "/register") # http:/127.0.0.1:5000/register
api.add_resource(UserDelete, "/userdelete/<string:username>") # http:/127.0.0.1:5000/userdelete/username
api.add_resource(StoreList, "/stores")

#if __name__ == "__main__":
#    db.init_app(app)
#    app.run(port=5000, debug=True)
