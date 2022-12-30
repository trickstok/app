from trickstok import DatabaseObject


class Notifications(DatabaseObject):

    def __init__(self, user, password, url):
        super().__init__(user, password, url)
        self.db = self.collection

    def add(self, to, content):
        self.db.notifications.insert_one({"to": to, "content": content})

    def get(self, to):
        return self.db.notifications.find({"to": to})

