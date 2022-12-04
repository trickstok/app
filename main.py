import json
import random
import re
import secrets

import conf
import flask
import requests
from flask import Flask, request, redirect, render_template, make_response, send_file, Response
from trickstok import Users, Videos

configuration = conf.asdict()
db_conf = {"user": configuration['App']['db_user'],  "password": configuration['App']['db_password'], "url": configuration['App']['db_url']}
users = Users(**db_conf, salt=configuration['App']['secret'])
videos = Videos(**db_conf)
app = Flask('Tricks Tok, The TikTok of Tricks')


def auth(template, **context):
    username = request.cookies.get('username')
    token = request.cookies.get('token')
    if username and token:
        user = users.find_by_username(username)
        if user['token'] == token:
            user['videos'] = videos.find_by_user(user['_id'])
            return render_template(template, **context, user=user)
    return redirect('/')


def is_logged():
    username = request.cookies.get('username')
    token = request.cookies.get('token')
    if username and token:
        user = users.find_by_username(username)
        if user['token'] == token:
            return True, user
    return False, {}


@app.route('/')
def presentation():
    return render_template('landing.html')


@app.route('/home')
def home():
    if request.args.get('video') is not None:
        video = videos.find_by_id(request.args.get('video'))
        return auth('index.html', video=video.video)
    logged, user = is_logged()
    if logged:
        return auth('index.html', video=videos.random(user['_id']).video)
    return redirect('/log')


@app.route('/admin')
def moderation():
    logged, user = is_logged()
    if logged:
        if user['administrator']:
            reports = videos.get_reported()
            return auth('admin.html', reports=reports)
    return redirect('/log')


@app.route('/u/<username>')
def user_page(username):
    user = users.find_by_username(username)
    user_videos = videos.find_by_user(user['_id'])
    return auth('profile.html', profile=user, videos=user_videos)


@app.route('/service-worker.js')
def sendWorker():
    return flask.send_file('static/js/pwa/service-worker.js')


@app.route('/log')
def connect():
    return render_template('connect.html')


@app.route('/reg')
def register_ui():
    return render_template('register.html')


@app.route('/login', methods=['POST'])
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


@app.route('/username-is-available')
def is_available():
    username = request.args.get('username')
    user = users.find_by_username(username)
    if user:
        return {"username": username, "available": False}
    return {"username": username, "available": True}


@app.route('/register', methods=['POST'])
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
    users.add(email, username, fullname, False, False, [], photo_string, bio, password)
    response = make_response(redirect('/home'))
    response.set_cookie('token', users.find_by_username(username)['token'])
    response.set_cookie('username', username)
    return response


@app.route('/add')
def addVideo():
    return auth('add.html')


@app.route('/post', methods=['POST'])
def postVideo():
    logged, user = is_logged()
    if logged:
        form = request.form
        description = form['desc']
        tags = form['tags'].split(',')
        video = request.files.get('video')
        video_id = secrets.token_urlsafe(16)
        video_ext = video.filename.split('.')[-1]
        video_string = f"{video_id}.{video_ext}"
        video.save(f'data/videos/{video_string}')
        videos.add(user['_id'], description, tags, video_string)
        return redirect(f'/home?video={video_string}')
    return redirect('/log')


@app.route('/comment/<video>', methods=['POST'])
def commentVideo(video):
    logged, user = is_logged()
    if logged:
        comment = request.form['comment']
        videos.find_by_id(video).add_comment(comment, user['_id'])
        return redirect(f'/home?video={video}')
    return redirect('/log')


@app.route('/signal/<video>', methods=['POST'])
def reportVideo(video):
    logged, user = is_logged()
    if logged:
        reason = request.form['reason']
        videos.find_by_id(video).report(reason, user['_id'])
        return redirect(f'/home?video={video}')
    return redirect('/log')


@app.route('/like/<video>', methods=['POST'])
def likeVideo(video):
    logged, user = is_logged()
    if logged:
        videos.find_by_id(video).like(user['_id'])
        return {"message": "Video liked successfully"}
    return {"message": "Error not connected"}


@app.route('/unlike/<video>', methods=['POST'])
def unlikeVideo(video):
    logged, user = is_logged()
    if logged:
        videos.find_by_id(video).unlike(user['_id'])
        return {"message": "Video liked successfully"}
    return {"message": "Error not connected"}


def stream(path):
    with open(path, "rb") as file:
        data = file.read(1024)
        while data:
            yield data
            data = file.read(1024)


@app.route('/media/<type>/<file>')
def deliver_media(type, file):
    logged, user = is_logged()
    if logged:
        if type == 'videos':
            videos.find_by_id(file).add_view(user['_id'])
            return Response(stream(f'data/{type}/{file}'))
        return send_file(f'data/{type}/{file}')
    return ""


@app.route('/watch')
def watch():
    logged, user = is_logged()
    if logged:
        if request.args.get('different_of') is not None:
            video = videos.random(user['_id'], request.args.get('different_of')).video
        else:
            video = videos.random(user['_id']).video
        return {"data": video}
    return {}


@app.route('/favicon.ico')
def favicon():
    return flask.send_file('static/assets/trickstok_logo_trans.png')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
