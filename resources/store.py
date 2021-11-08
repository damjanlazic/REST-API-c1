from flask_restful import Resource
from models.store import StoreModel
from flask_jwt import jwt_required


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {"message": "Store not found"}, 404

    @jwt_required()   
    def post(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return {"Store already exists"}, 400

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occured while creating a store"}, 500
        return store.json()


    @jwt_required()
    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
# for loop deletes all the items in that store, before we delete the store itself
# otherwise store would be deleted and all its items would still be there with store_id=null
            for item in store.items:
                item.delete_from_db()
            store.delete_from_db()
            return {"message": f"Store {name} deleted"}
        return {"message": "Store not found"}


class StoreList(Resource):
    @jwt_required()
    def get(self):
        return {"stores": [store.json_basic() for store in StoreModel.query.all()]}
