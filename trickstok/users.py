import datetime
import hashlib
import locale
import secrets
from zipfile import ZipFile, ZipInfo

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
        to_string = to
        if to:
            to_string = 'Toujours'
        ban_history.append({'from': from_date, 'to': to_string, 'by': by, 'reason': reason})
        self.db.users.update_one({'username': username}, {'$set': {'banned': to, 'ban_history': ban_history}})

    def search(self, keyword):
        results = self.db.users.find({"$text": {'$search': keyword}})
        users_results = []
        for user in results:
            del user['_id']
            del user['token']
            del user['password']
            users_results.append(user)
        return users_results

    def get_data_of(self, username, videos):
        user = self.db.users.find_one({'username': username})
        with ZipFile(f'data/{username}.zip', 'w') as zipfile:
            explications = """
Bravo tu as bien téléchargé tes données...
Nous allons t'expliquer comment est structurée cette archive contenant toutes les données que nous connaissons sur toi.

`/README.txt`: le fichier que tu lis actuellement, donne des informations sur la structure de cette archive
`/utilisateur.txt`: ce fichier contient les données concernant ton compte
`/avatar.png`: ta photo de profil

`/videos/`: ce dossier contient les données qui concernent les vidéos que tu as publié
`/videos/[video].[ext]`: le fichier vidéo 
`/videos/[video].[ext].txt`: les données de la vidéo 
`/videos/[video].[ext].comments.txt`: les commentaires de la vidéo 

`/commentaires/[video].[ext].comments.[comment_id].txt`: le commentaire [comment_id] que vous avez posté sur [video]
            """
            zipfile.writestr('README.txt', explications)
            bans = " | ".join([f"du {ban['from']} au {ban['to']} par le modérateur {ban['by']} pour {ban['reason']}" for ban in user['ban_history']])
            utilisateur = f"""
Nom complet:{user['fullname']}
Nom d'utilisateur trickstok:{user['username']}
Description:{user['description']}
Certifié:{user['certified']}
Administrateur:{user['administrator']}
Intérêts:{','.join(user['interests'])}
Token:{user['token']}
Mot de passe hashé:{user['password']}
Photo de profil:(fichier:avatar.png)
Bannissements:{bans}
            """
            zipfile.writestr("utilisateur.txt", utilisateur)
            zipfile.write(f"data/pdp/{user['photo']}", "avatar.png")
            for video in videos:
                video = video
                video_string = f"""
Description de la vidéo:{video['description']}
Tags de la vidéo:{','.join(video['tags'])}
Nombre de commentaires de la vidéo:{video['comment_count']}
Commentaires de la vidéo:(fichier:/videos/{video['video_id']}.comments.txt)
Nombre de likes de la vidéo:{video['likes_count']}
Nombre de vues de la vidéo:{video['views']}
Fichier vidéo:(fichier:/videos/{video['video_id']})
                """
                comments_string = """"""
                for comment in video['comments']:
                    comments_string += f"\"{comment['content']}\" par @{comment['user']['username']}\n"
                zipfile.write(f"data/videos/{video['video_id']}", f"videos/{video['video_id']}")
                zipfile.writestr(f"videos/{video['video_id']}.txt", video_string)
                zipfile.writestr(f"videos/{video['video_id']}.comments.txt", comments_string)
            for comment in self.db.comments.find({'user': user['_id']}):
                video_id = self.db.videos.find_one({"_id": comment['video']})
                if video_id:
                    video_id = video_id['video_id']
                else:
                    video_id = 'deleted'
                comments_string = f"""
                Tu as commenté "{comment['content']}" sur la vidéo https://trickstok.camarm.fr/home?video={video_id}
                """
                zipfile.writestr(f"commentaires/{video_id}.comments.{str(comment['_id'])}.txt", comments_string)
            zipfile.close()
            return f'data/{username}.zip'

    def certify(self, username):
        self.db.users.update_one({'username': username}, {'$set': {'certified': True}})

    def update(self, old_username, new_email, new_username, new_fullname, new_interests, photo_string, new_bio):
        self.db.users.update_one({'username': old_username}, {"$set": {
            "email": new_email,
            "username": new_username,
            "fullname": new_fullname,
            "interests": new_interests,
            "photo": photo_string,
            "description": new_bio
        }})

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
