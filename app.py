import os

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import User, UserRegister, UserLogin
from resources.items import Item, ItemList
from resources.store import Store, StoreList
from datetime import timedelta


app = Flask(__name__)

app.config["DEBUG"] = True

# to make this work in heroku, .replace() changes postgres into postgresql,
# this is needed as these libraries are not updated in Heroku, whereas postres was changed to postresql
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace("://", "ql://", 1)  #, "sqlite:///data.db")
#another approach is to add a new configuration variable in Heroku->settings, I named it DATABASE_URL_SPECIAL
# and copied contents of DATABASE_URL configuration variable in it, than changed postgres to postgresql:
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL_SPECIAL", "sqlite:///data.db")

# turns off the flask sqlalchemy modification tracker, because sqlalchemy has its own
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
# To allow flask propagating exception even if debug is set to false on app
app.config['PROPAGATE_EXCEPTIONS'] = True
# authentication doesn't work if you don't set a secret_key / can't get a token
app.secret_key = "Zia_the_battle_dog" 

# if you want app.secret_key and jwt_secret_key different than use:
# app.config["JWT_SECRET_KEY"] =...

# config JWT to expire within half an hour
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)

api = Api(app)


jwt = JWTManager(app) # does not automatically create and /auth endpoint, we do it ourselves

api.add_resource(Store, "/store/<string:name>")
api.add_resource(Item, "/item/<string:name>") #http://127.0.0.1:5000/item/itemsname
api.add_resource(ItemList, "/items") # http:/127.0.0.1:5000/items
api.add_resource(UserRegister, "/register") # http:/127.0.0.1:5000/register
api.add_resource(User, "/user/<int:user_id>") # http:/127.0.0.1:5000/user/user_id
api.add_resource(StoreList, "/stores")
api.add_resource(UserLogin, "/login")

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    
    if app.config["DEBUG"]:
        @app.before_first_request
        def create_tables():
            db.create_all()

    app.run(port=5000, debug=True)
