from db import db

class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

# lazy... makes it not create an object for each item column all at once
    items = db.relationship('ItemModel', lazy='dynamic')

    def __init__(self, name):
        self.name = name

# returning a list of items for every store is not really practical if listing all the stores
# when there are many stores with many items:
    def json_basic(self): 
        return {"name": self.name, "id": self.id}

# need a query builder: self.items.all() returns a list of objects
    def json(self):    
        return {"name": self.name, "items": [item.json() for item in self.items.all()], "id": self.id}
# if you don't use lazy='dynamic' then it autmatically creates an object
# for each item, which can take lots of time if you have many items:
#       return {"name": self.name, "items": [item.json() for item in self.items}

    @classmethod
    def find_by_name(cls, name):
# this makes the query filters from the database and limits the results to 1
# it also creates an object of the ItemModel class and populates its parameters name and price
        return cls.query.filter_by(name=name).first()
# all the code from section5 is replaced by the above return statement

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
