from app import app
from db import db

db.init_app(app)

# this automatically creates all the required tables in the data.db file if they don't exist already
# it happens immediately before the first request is made,
@app.before_first_request
def create_tables():
    db.create_all()