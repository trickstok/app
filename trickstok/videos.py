from pymongo.collection import ObjectId
from trickstok import DatabaseObject, Users


class Videos(DatabaseObject):

    def __init__(self, user, password, url):
        super().__init__(user, password, url)
        self.db = self.collection

    def add(self, user, description, tags, video_id):
        self.db.videos.insert_one({
            "user": user,
            "description": description,
            "tags": tags,
            "video_id": video_id
        })

    def get_reported(self):
        reported = self.db.reports.find()
        for report in reported:
            report['video'] = self.find_by_id(report['video'])
        return reported

    def find_by_object_id(self, _id):
        return Video(self.db.videos.find_one({"_id": ObjectId(_id)}), self.db)

    def find_by_id(self, _id):
        return Video(self.db.videos.find_one({"video_id": _id}), self.db)

    def find_by_user(self, _id):
        return [Video(video, self.db).video for video in self.db.videos.find({"user": _id})]

    def find_viewed_by_user(self, _id, in_list=False):
        views = self.db.views.find({'user': _id})
        if not in_list:
            return [Video(self.db.videos.find({"_id": viewed['video']}), self.db).video for viewed in views]
        return [viewed['video'] for viewed in views]

    def find_liked_by_user(self, _id):
        views = self.db.views.find({'user': _id, 'liked': True})
        return [Video(self.db.videos.find({"_id": viewed['video']}), self.db).video for viewed in views]

    def find_not_viewed_by_user(self, _id, in_list=False):
        viewed = self.find_viewed_by_user(_id, True)
        not_viewed = self.db.videos.find({'_id': {"$not": {"$in": [viewed]}}})
        if not in_list:
            return [Video(self.db.videos.find({"_id": not_view['_id']}), self.db).video for not_view in not_viewed]
        return [not_view['_id'] for not_view in not_viewed]

    def is_liked(self, video, user):
        video = self.db.views.find_one({'video': video, 'user': user})
        if video:
            return video['liked']
        return False

    def random(self, user, different_from=None):
        if different_from is not None:
            video = list(self.db.videos.aggregate([
                {"$sample": {"size": 1}}
            ]))[0]
            while video['video_id'] == different_from:
                video = list(self.db.videos.aggregate([
                    {"$sample": {"size": 1}}
                ]))[0]
            video['liked'] = self.is_liked(video['_id'], user)
            return Video(video, self.db)
        not_viewed = self.find_not_viewed_by_user(user, True)
        if len(not_viewed) == 0:
            video = list(self.db.videos.aggregate([
                {"$sample": {"size": 1}}
            ]))[0]
        else:
            video = self.db.videos.find_one({'_id': not_viewed[0]})
        video['liked'] = self.is_liked(video['_id'], user)
        # video_user = self.db.users.find_one({'_id': video['user']})
        # while video_user['banned']:
        #     video = list(self.db.videos.aggregate([
        #         {"$sample": {"size": 1}}
        #     ]))[0]
        #     if self.db.view.find_one({"video": video['_id'], "user": user}) is not None:
        #         video = list(self.db.videos.aggregate([
        #             {"$sample": {"size": 1}}
        #         ]))[0]
        return Video(video, self.db)


class Video:

    def __init__(self, video, db):
        self.db = db
        self.video = video
        self.video['user'] = self.db.users.find_one({'_id': video['user']})
        self.video['comments'] = self.get_comments()
        self.video['comment_count'] = len(self.video['comments'])
        self.video['likes_count'] = self.db.views.count_documents({"video": self.video['_id'], "liked": True})
        self.video['views'] = self.db.views.count_documents({"video": self.video['_id']})
        self.video_object_id = video['_id']
        del self.video['_id']
        del self.video['user']['token']
        del self.video['user']['password']
        del self.video['user']['_id']

    def add_comment(self, comment, user_id):
        self.db.comments.insert_one({
            "video": self.video_object_id,
            "user": user_id,
            "content": comment
        })

    def add_view(self, user):
        has_been_viewed = self.db.views.find_one({'video': self.video_object_id, 'user': user})
        if has_been_viewed is not None:
            return
        self.db.views.insert_one({'video': self.video_object_id, 'user': user, 'liked': False})

    def like(self, user):
        self.db.views.update_one({'video': self.video_object_id, 'user': user}, {'$set': {'liked': True}})

    def unlike(self, user):
        self.db.views.update_one({'video': self.video_object_id, 'user': user}, {'$set': {'liked': False}})

    def report(self, reason, user_id):
        self.db.reports.insert_one({
            "video": self.video_object_id,
            "user": user_id,
            "reason": reason
        })

    def get_comments(self):
        comments = list(self.db.comments.find({"video": self.video["_id"]}))
        for comment in comments:
            user = self.db.users.find_one({'_id': comment['user']})
            del user['password']
            del user['token']
            del comment['_id']
            user['_id'] = str(user['_id'])
            comment["user"] = user
            comment["video"] = str(comment["video"])
        return comments

    def delete(self):
        self.db.comments.delete_many({})
