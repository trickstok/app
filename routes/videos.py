from utils import *


class VideosRoutes(Route):

    def __init__(self, app):
        super().__init__('Videos Routes', 'All routes used for videos pages and utilities...')
        self.app = app

    def build(self):
        @self.app.route('/add')
        def addVideo():
            return auth('add.html')

        @self.app.route('/delete/<video>')
        def deleteVideo(video):
            logged, user = is_logged()
            if logged:
                video = videos.find_by_id(video)
                if video.video['user']['username'] == user['username']:
                    video.delete()
                    return redirect('/home#account')
                elif user['administrator']:
                    video_user = video.video['user']
                    administrator = user['username']
                    content = f"Ta vidéo avec la description \"{video.video['description']}\" à été supprimée par l'administrateur @{administrator}.<br>Pour plus d'information à ce propos tu peux nous contacter..."
                    mails.send_mail(video_user['email'], 'Ta vidéo à été supprimée', templates.base.format(email=video_user['username'], content=content))
                    video.delete()
                    return redirect('/admin')
            return redirect('/log')

        @self.app.route('/post', methods=['POST'])
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

        @self.app.route('/comment/<video>', methods=['POST'])
        def commentVideo(video):
            logged, user = is_logged()
            if logged:
                comment = request.form['comment']
                videos.find_by_id(video).add_comment(comment, user['_id'])
                return redirect(f'/home?video={video}&nl=nl')
            return redirect('/log')

        @self.app.route('/signal/<video>', methods=['POST'])
        def reportVideo(video):
            logged, user = is_logged()
            if logged:
                reason = request.form['reason']
                videos.find_by_id(video).report(reason, user['_id'])
                return redirect(f'/home?video={video}&nl=nl')
            return redirect('/log')

        @self.app.route('/like/<video>')
        def likeVideo(video):
            logged, user = is_logged()
            if logged:
                videos.find_by_id(video).like(user['_id'])
                return {"message": "Video liked successfully"}
            return {"message": "Error not connected"}

        @self.app.route('/unlike/<video>')
        def unlikeVideo(video):
            logged, user = is_logged()
            if logged:
                videos.find_by_id(video).unlike(user['_id'])
                return {"message": "Video liked successfully"}
            return {"message": "Error not connected"}

        @self.app.route('/search')
        def search():
            query = request.args.get('q')
            if query:
                users_results = users.search(query)
                video_results = videos.search(query)
                return {"msg": "Search in trickstok successfully", "data": {"users": users_results, "videos": video_results}}
            return {"msg": "Please provide a query (q=)", "data": []}