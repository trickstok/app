import datetime
import locale
import conf
from flask import Flask, request, redirect, render_template
from trickstok import Users, Videos, Mailer, Template, Messages
import ast


locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
configuration = conf.asdict()
db_conf = {"user": configuration['App']['db_user'],  "password": configuration['App']['db_password'], "url": configuration['App']['db_url']}
users = Users(**db_conf, salt=configuration['App']['secret'])
videos = Videos(**db_conf)
mails = Mailer(**db_conf)
messages = Messages(**db_conf)
templates = Template()
mailing_lists = configuration['App']['mailing_lists'].split(',')
app = Flask('Tricks Tok, The TikTok of Tricks')


class Route:

    def __init__(self, name, description):
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description


def auth(template, **context):
    username = request.cookies.get('username')
    token = request.cookies.get('token')
    if username and token:
        user = users.find_by_username(username)
        if user['token'] == token and user['banned'] == False:
            user['videos'] = videos.find_by_user(user['_id'])
            del user['ban_history']
            return render_template(template, **context, user=user)
    return redirect('/')


def is_logged():
    username = request.cookies.get('username')
    token = request.cookies.get('token')
    if username and token:
        user = users.find_by_username(username)
        if user['token'] == token and user['banned'] == False:
            return True, user
    return False, {}
