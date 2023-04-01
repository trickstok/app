from trickstok import DatabaseObject


class Messages(DatabaseObject):

    notification = "@NOTIFICATIONS@"

    def __init__(self, user, password, url):
        super().__init__(user, password, url)
        self.db = self.collection

    @staticmethod
    def generate_content_object(type_object, **kwargs):
        if type_object == 'video':
            return {"_id": kwargs['_id'], "desc": kwargs['description'], "data_type": 'video'}

    def add(self, from_username, to_username, content, additional_content):
        self.db.notifications.insert_one({"to": to_username, "content": content, "options": [additional_content], "read": False, "from": from_username})

    def get(self, username, include_read=True):
        if include_read:
            messages = list(self.db.notifications.find({"$or": [{"to": username, "from": {"$not": {"$in": [self.notification]}}}, {"to": {"$not": {"$in": [self.notification]}}, "from": username}]}))
        else:
            messages = list(self.db.notifications.find({"$or": [{"to": username, "from": {"$not": {"$in": [self.notification]}}, "read": False}, {"to": {"$not": {"$in": [self.notification]}}, "from": username, "read": False}]}))
        chats = []
        for message in messages:
            if message['from'] not in chats and message['from'] != username:
                chats.append(message['from'])
            if message['to'] not in chats and message['to'] != username:
                chats.append(message['to'])
        chats_messages = {f"{chat}": [] for chat in chats}
        for message in messages:
            message['from'] = self.db.users.find_one({"username": message['from']})
            message['to'] = self.db.users.find_one({"username": message['to']})
            del message['from']['password']
            del message['from']['token']
            del message['from']['_id']
            del message['from']['ban_history']
            del message['to']['password']
            del message['to']['token']
            del message['to']['_id']
            del message['to']['ban_history']
            message['_id'] = str(message['_id'])
            if message['from']['username'] == username:
                chats_messages[message['to']['username']].append(message)
                continue
            chats_messages[message['from']['username']].append(message)
        return chats_messages

    def getNotification(self, to_username, include_read=True):
        if include_read:
            return list(self.db.notifications.find({"to": to_username, "from": self.notification}))
        return list(self.db.notifications.find({"read": False, "to": to_username, "from": self.notification}))
