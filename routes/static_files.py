from utils import *
import flask


class StaticFilesRoutes(Route):

    def __init__(self, app):
        super().__init__('Static Files Routes', 'All routes used for legals and utils files...')
        self.app = app

    def build(self):
        @self.app.route('/favicon.ico')
        def favicon():
            return flask.send_file('static/assets/trickstok_logo_trans.png')

        @self.app.route('/service-worker.js')
        def sendWorker():
            return flask.send_file('static/js/pwa/service-worker.js')

        @self.app.route('/licence')
        def licence():
            return flask.send_file('LICENSE')

        @self.app.route('/download')
        def downloadApp():
            return flask.send_file('mobile-app/app/release/app-release.apk')

        @self.app.route('/terms')
        def termsAndConditions():
            return render_template('terms_and_conditions.html')

        @self.app.route('/cgu')
        def CGU():
            return render_template('cgu.html')
