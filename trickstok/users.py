import hashlib
import secrets
from pymongo.collection import ObjectId
from trickstok import DatabaseObject


class Users(DatabaseObject):

    def __init__(self, user, password, url, salt):
        super().__init__(user, password, url)
        self.db = self.collection
        self.salt = salt

    def add(self, email, username, fullname, administrator, certified, interests, photo, description, password):
        if not self.find_by_username(username):
            token = secrets.token_urlsafe(32)
            hashed = hashlib.scrypt(password.encode(), salt=self.salt.encode(), n=2, r=64, p=4)
            self.db.users.insert_one({
                "email": email,
                "username": username,
                "fullname": fullname,
                "administrator": administrator,
                "token": token,
                "certified": certified,
                "interests": interests,
                "ban_history": [

                ],
                "banned": False,
                "photo": photo,
                "description": description,
                "password": hashed
            })

    def login(self, username, password):
        user = self.find_by_username(username)
        if user:
            hashed = hashlib.scrypt(password.encode(), salt=self.salt.encode(), n=2, r=64, p=4)
            if hashed == user['password']:
                return True, user
        return False, {}

    def find_by_id(self, _id):
        return self.db.users.find_one({"_id": ObjectId(_id)})

    def find_by_username(self, username):
        return self.db.users.find_one({"username": username})
