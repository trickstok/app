import os

from utils import *
from flask import send_file, request, redirect, make_response
import re
import secrets


class UserRoutes(Route):

    def __init__(self, app):
        super().__init__('User Routes', 'All routes used for user(s) pages and utilities...')
        self.app = app

    def build(self):

        @self.app.route('/home')
        def home():
            logged, user = is_logged()
            no_loader = True if request.args.get('nl') == 'nl' else False
            if request.args.get('video') is not None:
                video = videos.find_by_id(request.args.get('video'))
                video_id = video.video_object_id
                video = video.video
                if user:
                    video['liked'] = videos.is_liked(video_id, user['_id'])
                else:
                    video['liked'] = False
                return auth('index.html', video=video, no_loader=no_loader)
            if logged:
                return auth('index.html', video=videos.random(user['_id']).video, no_loader=no_loader)
            return redirect('/log')

        @self.app.route('/u/<username>')
        def userPage(username):
            user = users.find_by_username(username)
            user_videos = videos.find_by_user(user['_id'])
            return auth('profile.html', profile=user, videos=user_videos)

        @self.app.route('/log')
        def connect():
            return render_template('connect.html')

        @self.app.route('/login', methods=['POST'])
        def login():
            form = request.form
            username = form['username']
            password = form['password']
            user = users.login(username, password)
            if user[0]:
                response = make_response(redirect('/home'))
                response.set_cookie('token', user[1]['token'])
                response.set_cookie('username', user[1]['username'])
                return response
            return redirect('/log')

        @self.app.route('/register', methods=['POST'])
        def register():
            form = request.form
            username = form['username']
            username = re.sub("[^a-z0-9_.]", "", username)
            email = form['email']
            fullname = form['fullname']
            bio = form['bio']
            password = form['password']
            photo = request.files['photo']
            photo_ext = photo.filename.split('.')[-1]
            photo_id = secrets.token_urlsafe(16)
            photo_string = f"{photo_id}.{photo_ext}"
            photo.save(f'data/pdp/{photo_string}')
            photo_url = upload_to_cdn(f'data/pdp/{photo_string}')
            os.remove(f'data/pdp/{photo_string}')
            users.add(email, username, fullname, False, False, [], photo_url, bio, password)
            response = make_response(redirect('/home'))
            response.set_cookie('token', users.find_by_username(username)['token'])
            response.set_cookie('username', username)
            return response

        @self.app.route('/reg')
        def registerUi():
            return render_template('register.html')

        @self.app.route('/username-is-available')
        def isAvailable():
            username = request.args.get('username')
            user = users.find_by_username(username)
            if user:
                return {"username": username, "available": False}
            return {"username": username, "available": True}

        @self.app.route('/modify', methods=['POST'])
        def updateProfile():
            logged, user = is_logged()
            if logged:
                form = request.form
                username = form['username']
                username = re.sub("[^a-z0-9_.]", "", username)
                email = form['email']
                fullname = form['fullname']
                bio = form['bio']
                interests = form['interests'].split(',')
                if request.files.get('photo'):
                    photo = request.files.get('photo')
                    photo_ext = photo.filename.split('.')[-1]
                    photo_id = secrets.token_urlsafe(16)
                    photo_string = f"{photo_id}.{photo_ext}"
                    photo.save(f'data/pdp/{photo_string}')
                    photo_url = upload_to_cdn(f'data/pdp/{photo_string}')
                    os.remove(f'data/pdp/{photo_string}')
                else:
                    photo_url = user['photo']
                users.update(user['username'], email, username, fullname, interests, photo_url, bio)
                return redirect('/home#account')
            return redirect('/log')

        @self.app.route('/get-my-data')
        def getUserDatas():
            logged, user = is_logged()
            if logged:
                user_videos = videos.find_by_user(user['_id'])
                return send_file(users.get_data_of(user['username'], user_videos))
            return redirect('/log')

