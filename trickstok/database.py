import pymongo


class DatabaseObject:

    def __init__(self, user, password, url):
        self.client = pymongo.MongoClient(f'mongodb+srv://{user}:{password}@{url}')
        self.collection = self.client.trickstok

    @property
    def users(self):
        return self.collection.users
