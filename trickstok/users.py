import datetime
import hashlib
import locale
import secrets
from pymongo.collection import ObjectId
from trickstok import DatabaseObject


locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

class Users(DatabaseObject):

    def __init__(self, user, password, url, salt):
        super().__init__(user, password, url)
        self.db = self.collection
        self.salt = salt

    @property
    def total(self):
        return self.db.users.count_documents({})

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

    def ban(self, username, to, from_date, by, reason):
        user = self.find_by_username(username)
        ban_history = user['ban_history']
        ban_history.append({'from': from_date, 'to': to, 'by': by, 'reason': reason})
        self.db.users.update_one({'username': username}, {'$set': {'banned': to, 'ban_history': ban_history}})

    def certify(self, username):
        self.db.users.update_one({'username': username}, {'$set': {'certified': True}})

    def login(self, username, password):
        user = self.find_by_username(username)
        if user:
            hashed = hashlib.scrypt(password.encode(), salt=self.salt.encode(), n=2, r=64, p=4)
            if hashed == user['password']:
                if user['banned'] == False:
                    return True, user
                elif user['banned'] == True:
                    return False, {}
                else:
                    banned_to = user['banned']
                    today = datetime.datetime.now()
                    if banned_to <= today:
                        self.db.users.update_one({'username': user['username']}, {'$set': {'banned': False}})
                        return True, user
        return False, {}

    def find_by_id(self, _id):
        return self.db.users.find_one({"_id": ObjectId(_id)})

    def find_by_username(self, username):
        return self.db.users.find_one({"username": username})
