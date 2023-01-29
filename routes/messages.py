from utils import *
from flask import request, redirect


class MessagesRoutes(Route):

    def __init__(self, app):
        super().__init__('User Routes', 'All routes used for user(s) pages and utilities...')
        self.app = app

    def build(self):

        @self.app.route('/send-message', methods=['POST'])
        def sendMessage():
            logged, user = is_logged()
            if logged:
                from_username = user['username']
                form = request.form
                to_username = users.find_by_username(form['to'])['username']
                messages.add(from_username, to_username, form['content'], [])
                return {"message": "Message successfully sent"}
            return redirect('/log')

        @self.app.route('/get-new-messages')
        def getMessages():
            logged, user = is_logged()
            if logged:
                username = user['username']
                msg = messages.get(username, False)
                notifications = messages.getNotification(username, False)
                return {"message": "Messages successfully received", "data": {"messages": msg, "notifications": notifications}}
            return redirect('/log')
