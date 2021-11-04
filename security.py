from models.user import UserModel

# for python 2.7 because of possible issues of encoding
from werkzeug.security import safe_str_cmp


def authenticate(username, password):
# same as: user = username_mapping["username"] but returns None if no such user exists    
    user = UserModel.find_by_username(username)
# same as if user is not None and ...

#    if user and user.password == password:
# safer way of comparing strings especially on older python versions:
    if user and safe_str_cmp(user.password, password):
        return user

def identity(payload):
    user_id = payload["identity"]
    return UserModel.find_by_id(user_id)

