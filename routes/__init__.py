import sys

from routes.admin import *
from routes.videos import *
from routes.video_files import *
from routes.user import *
from routes.trickstok import *
from routes.static_files import *
from routes.messages import *


__routes_classes__ = [AdminRoutes, VideosRoutes, UserRoutes, VideoFilesRoutes, BasicRoutes, StaticFilesRoutes, MessagesRoutes]


def build(app):
    for route_class in __routes_classes__:
        built = route_class(app)
        try:
            print(f'\033[1mBuilding {built.name}\033[0m\n{built.description}\n')
            built.build()
        except Exception as err:
            print(f'\033[91mFailed to build {built.name}\033[0m')
            raise err


def run(app):
    build(app)
    debug = False
    port = int(configuration['App']['port'])
    if '--debug' in sys.argv:
        debug = True
    if '--secure' in sys.argv:
        app.run(debug=debug, threaded=True, host='0.0.0.0', port=port, ssl_context=('certificate.pem', 'privatekey.pem'))
    else:
        app.run(debug=debug, threaded=True, host='0.0.0.0', port=port)
