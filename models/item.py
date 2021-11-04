from db import db
#from sqlalchemy.engine import create_engine


class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float(precision=2))

    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))
    store = db.relationship("StoreModel")

    def __init__(self, name, price, store_id):
        self.name = name
        self.price = price
        self.store_id = store_id

    def json(self):
        return {"name": self.name, "price": self.price, "store_id": self.store_id}

    @classmethod
    def find_by_name(cls, name):
# this makes the query filters from the database and limits the results to 1
# it also creates an object of the ItemModel class and populates its parameters name and price
        return cls.query.filter_by(name=name).first()
# all the code from section5 is replaced by the above return statement


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
