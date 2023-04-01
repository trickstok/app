import os
import re
from utils import *
from flask import send_file


class VideoFilesRoutes(Route):

    def __init__(self, app):
        super().__init__('Video Files Routes', 'All routes used for videos delivery...')
        self.app = app

    def build(self):
        def stream(path):
            headers = request.headers
            if "range" not in headers:
                return app.response_class(status=400)
        
            video_path = os.path.abspath(path)
            size = os.stat(video_path)
            size = size.st_size
        
            chunk_size = 10**3
            start = int(re.sub("\D", "", headers["range"]))
            end = min(start + chunk_size, size - 1)
        
            content_length = end - start + 1
        
            def get_chunk(chunk_video_path, chunk_start, chunk_end):
                with open(chunk_video_path, "rb") as f:
                    f.seek(chunk_start)
                    chunk = f.read(chunk_end)
                return chunk
        
            headers = {
                "Content-Range": f"bytes {start}-{end}/{size}",
                "Accept-Ranges": "bytes",
                "Content-Length": content_length,
                "Content-Type": "video/mp4",
            }
        
            return app.response_class(get_chunk(video_path, start, end), 206, headers)

        @self.app.route('/media/<filetype>/<file>')
        def deliverMedia(filetype, file):
            logged, user = is_logged()
            if logged:
                if filetype == 'videos':
                    if file != 'banned.mp4':
                        videos.find_by_id(file).add_view(user['_id'])
                    return stream(f'data/{filetype}/{file}')
                return send_file(f'data/{filetype}/{file}')
            return ""

        @self.app.route('/media/videos/<video>/thumbnail')
        def deliverThumbnail(video):
            logged, user = is_logged()
            if logged:
                return send_file(f'data/thumbnails/{video}.png')
            return ""

        @self.app.route('/watch')
        def watch():
            logged, user = is_logged()
            if logged:
                if request.args.get('different_of') is not None:
                    video = videos.random(user['_id'], request.args.get('different_of'))
                else:
                    video = videos.random(user['_id'])
                video.add_view(user['_id'])
                return {"data": video.video}
            return {}
