import pymongo


class DatabaseObject:

    def __init__(self, user, password, url):
        self.client = pymongo.MongoClient(f'mongodb+srv://{user}:{password}@{url}')
        self.collection = self.client.trickstok
        self.client.trickstok.videos.create_index([('description', 'text'), ('tags', 'text')], default_language='french')
        self.client.trickstok.users.create_index([('username', 'text'), ('name', 'text'), ('description', 'text')], default_language='french')

    @property
    def users(self):
        return self.collection.users

    @property
    def videos(self):
        return self.collection.videos
