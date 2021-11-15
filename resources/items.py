# import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
#from werkzeug.exceptions import InternalServerError
from models.item import ItemModel
from models.store import StoreModel

class Item(Resource):
#        data = request.get_json(silent=True)
# instead use parser, to make sure only "price" is passed as an argument
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help="This field has to be a number greater than 0"
    )
    parser.add_argument(
        "store_id",
        type=int,
        required=True,
        help="Every item needs to be assigned to a particular store via the store_id number, for more info see the list of available stores"
    )


    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item is None:
            return {"message": "Item not found"}, 404

        return item.json()

    @jwt_required()
    def post(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return {"message": "Item already exists"}

        # return terminates the method so, we don't need the else statement
        data = Item.parser.parse_args()
        item = ItemModel(name, **data) # data["price"], data["store_id"]

# so that you can't add an item with a nonexistant store_id number:      
        if StoreModel.find_by_id(item.store_id):
            try:
                if item.price>0:
                    item.save_to_db()
                else:
                    return {"message": "This is not Salvation Army, we don't do giveaways"}
            except:
                return {"message": "An error occured inserting the item"}, 500
            return item.json(), 201
        return {"message": "Store with id: {} does not exist!".format(item.store_id)}

    @jwt_required()
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": "Item deleted"}
        return {"message": "Item not found"}


    @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args() #parser defined in the Item class, so it's a property of all objects, can be accessed by all methods
#        data = request.get_json(silent=True)
        item = ItemModel.find_by_name(name)
        try:
            price = float(data["price"])
            if data["price"]<=0:
                return {"message": "price has to be greater than 0"}
        except:
            return {"message": "Price has to be number! (digits and that sort of stuff)"}
        if item:
            item.price = price
            item.store_id = data["store_id"]
        else:
            item = ItemModel(name, **data) # data["price"], data["store_id"]
# so that you can't add an item with a nonexistant store_id number:        
        if StoreModel.find_by_id(item.store_id):
            item.save_to_db()
            return item.json() #,200?
        return {"message": "Store with id: {} does not exist!".format(item.store_id)}, 404

class ItemList(Resource):
    def get(self):
        return {"items :" : [item.json() for item in ItemModel.find_all()]}
    
# same using lambda and map() - less pythonic but good if collaborating with JavaScripters and such
# lambda returns the value x.json() while map applies the lambda function to every element of the second argument
        return{"items :" : list(map(lambda x: x.json(), ItemModel.query.all()))}

# same without list comprehension        
        items = ItemModel.query.all() 
        item_list = []
        for item in items:
            print("name", item.name)
            item_list.append(item.json())
        return {"items: " : item_list}     

# same without SQLAlchemy        
        items = []
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        select_query = "SELECT * FROM items"
        for row in cursor.execute(select_query):
            item = {"store_id": row[0], "name": row[1], "price": row[2]}
            items.append(item)

        connection.close()

        return {"items" : items}
