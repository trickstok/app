import datetime
import locale
import os
import re
import secrets
import sys
import conf
import flask
import markdown
from flask import Flask, request, redirect, render_template, make_response, send_file
from trickstok import Users, Videos, Mailer, Template, Notifications

locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
configuration = conf.asdict()
db_conf = {"user": configuration['App']['db_user'],  "password": configuration['App']['db_password'], "url": configuration['App']['db_url']}
users = Users(**db_conf, salt=configuration['App']['secret'])
videos = Videos(**db_conf)
mails = Mailer(**db_conf)
notifications = Notifications(**db_conf)
templates = Template()
mailing_lists = configuration['App']['mailing_lists'].split(',')
app = Flask('Tricks Tok, The TikTok of Tricks')


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


def get_article(name):
    post_file = open(f'blog/{name}')
    content = "".join(post_file.readlines()[1:])
    content = markdown.markdown(content)
    post_file.seek(0)
    meta_datas = post_file.readline()
    date, title, cover = meta_datas.split(';')
    day, month, year = date.split('-')
    date = datetime.datetime(year=int(year), month=int(month), day=int(day)).strftime("%A %-d %B")
    return {'title': title, 'date': date, 'content': content, 'cover': cover, 'name': name.split('.')[0]}


def get_articles():
    all_posts = os.listdir('blog/')
    articles = []
    for post in all_posts:
        if os.path.isfile(f'blog/{post}') and post not in 'draft':
            articles.append(get_article(post))
    return articles


@app.route('/')
def presentation():
    return render_template('landing.html')


@app.route('/blog')
def blog():
    if request.args.get('post') is None:
        articles = get_articles()
        return render_template('blog_index.html', articles=articles)
    post = request.args.get('post')
    if os.path.isfile(f'blog/{post}.md'):
        article = get_article(f'{post}.md')
    else:
        article = {'title': "Erreur 404; Article introuvable", 'date': "Erreur 404; Article introuvable", "content": "<h1>404 article introuvable</h1><br><p>Cet article à été déplacé ou supprimé...</p>", 'cover': "/static/assets/posts/404.png"}
    articles = get_articles()
    return render_template('blog.html', **article, articles=articles)


@app.route('/home')
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


@app.route('/prelogin', methods=['POST'])
def betaAccess():
    form = request.form
    email = form['email']
    content = templates.base.format(email=email, content=templates.betalog)
    mails.add_to_list(email, 'beta', mails.send_mail, args={"to": email, "subject": 'Tu a bien été préinscris !', "content": content})
    return redirect('/')


@app.route('/admin')
def moderation():
    logged, user = is_logged()
    if logged:
        if user['administrator']:
            success = None
            if request.args.get('success'):
                success = True if request.args.get('success') == 'y' else False
            reports = videos.get_reported()
            users_nb = users.total
            videos_nb = videos.total
            views_nb = videos.total_views
            reports_nb = videos.total_reports
            notifs = notifications.get('admins')
            return auth('admin.html', success=success, reports=reports, users_nb=users_nb, videos_nb=videos_nb, views_nb=views_nb, reports_nb=reports_nb, notifs=notifs)
    return redirect('/log')


@app.route('/admin/users')
def moderationUsers():
    logged, user = is_logged()
    if logged:
        if user['administrator']:
            if request.args.get('user') is not None:
                username = request.args.get('user')
                user = users.find_by_username(username)
                return auth('admin_users.html', result=user)
            return auth('admin_users.html', result=None)
    return redirect('/log')


@app.route('/admin/mails')
def moderationMails():
    logged, user = is_logged()
    if logged:
        if user['administrator']:
            campagnes = mailing_lists
            total = mails.total
            mailing_campagnes = []
            for liste in campagnes:
                emails = list(mails.get_list_mails(liste))
                mailing_campagnes.append({'name': liste, 'mails': emails, 'number': len(emails)})
            return auth('admin_mails.html', campagnes=mailing_campagnes, total=total)
    return redirect('/log')


@app.route('/admin/report/<report>', methods=['POST'])
def moderationDeleteReport(report):
    logged, user = is_logged()
    if logged:
        if user['administrator']:
            videos.delete_report(report)
            return redirect('/admin')
    return redirect('/log')


@app.route('/admin/ban', methods=['POST'])
def banUser():
    logged, user = is_logged()
    if logged:
        if user['administrator']:
            form = request.form
            today = datetime.datetime.now()
            username = form['username']
            reason = form['reason']
            user_email = users.find_by_username(username)['email']
            to = form['to']
            if to == 'always':
                date = True
            elif to == 'week':
                date = today + datetime.timedelta(weeks=1)
            elif to == 'month':
                date = today + datetime.timedelta(weeks=4)
            elif to == '2month':
                date = today + datetime.timedelta(weeks=4 * 2)
            elif to == '5month':
                date = today + datetime.timedelta(weeks=4 * 5)
            else:
                date = True
            users.ban(username, date, today, user['username'], reason)
            if date and type(date) == bool:
                ban_type = 'définitif'
                after = '.'
            else:
                ban_type = 'temporaire'
                today_string = today.strftime("%A %-d %B")
                date_string = date.strftime("%A %-d %B")
                after = f' et durera du {today_string} au {date_string}.'
            content = templates.banned.format(type=ban_type, end=after, reason=reason)
            mails.send_mail(user_email, 'TricksTok - Bannissement', content)
            return redirect('/admin?success=y')
    return redirect('/log')


@app.route('/ask-certify', methods=['POST'])
def askCertify():
    logged, user = is_logged()
    if logged:
        form = request.form
        why = form['why']
        email = user['email']
        mails.send_mail(email, 'Demande de certification prise en compte', templates.base.format(email=email, content=f"Nous avons bien reçu ta demande de certification pour le compte trickstok @{user['username']}.<br>Nous traiterons ta demande sous peu..."))
        notifications.add('admins', f"Demande de certification de @{user['username']}.\n\n{why}")
        return redirect(f'/home#account')
    return redirect('/log')


@app.route('/admin/certify', methods=['POST'])
def certifyUser():
    logged, user = is_logged()
    if logged:
        if user['administrator']:
            form = request.form
            username = form['username']
            users.certify(username)
            return redirect('/admin?success=y')
    return redirect('/log')


@app.route('/u/<username>')
def userPage(username):
    user = users.find_by_username(username)
    user_videos = videos.find_by_user(user['_id'])
    return auth('profile.html', profile=user, videos=user_videos)


@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        users_results = users.search(query)
        video_results = videos.search(query)
        return {"msg": "Search in trickstok successfully", "data": {"users": users_results, "videos": video_results}}
    return {"msg": "Please provide a query (q=)", "data": []}


@app.route('/log')
def connect():
    return render_template('connect.html')


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


@app.route('/reg')
def registerUi():
    return render_template('register.html')


@app.route('/username-is-available')
def isAvailable():
    username = request.args.get('username')
    user = users.find_by_username(username)
    if user:
        return {"username": username, "available": False}
    return {"username": username, "available": True}


@app.route('/modify', methods=['POST'])
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
        else:
            photo_string = user['photo']
        users.update(user['username'], email, username, fullname, interests, photo_string, bio)
        return redirect('/home#account')
    return redirect('/log')


@app.route('/get-my-data')
def getUserDatas():
    logged, user = is_logged()
    if logged:
        user_videos = videos.find_by_user(user['_id'])
        return send_file(users.get_data_of(user['username'], user_videos))
    return redirect('/log')


@app.route('/add')
def addVideo():
    return auth('add.html')


@app.route('/delete/<video>')
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
        return redirect(f'/home?video={video}&nl=nl')
    return redirect('/log')


@app.route('/signal/<video>', methods=['POST'])
def reportVideo(video):
    logged, user = is_logged()
    if logged:
        reason = request.form['reason']
        videos.find_by_id(video).report(reason, user['_id'])
        return redirect(f'/home?video={video}&nl=nl')
    return redirect('/log')


@app.route('/like/<video>')
def likeVideo(video):
    logged, user = is_logged()
    if logged:
        videos.find_by_id(video).like(user['_id'])
        return {"message": "Video liked successfully"}
    return {"message": "Error not connected"}


@app.route('/unlike/<video>')
def unlikeVideo(video):
    logged, user = is_logged()
    if logged:
        videos.find_by_id(video).unlike(user['_id'])
        return {"message": "Video liked successfully"}
    return {"message": "Error not connected"}


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


@app.route('/media/<filetype>/<file>')
def deliverMedia(filetype, file):
    logged, user = is_logged()
    if logged:
        if filetype == 'videos':
            if file != 'banned.mp4':
                videos.find_by_id(file).add_view(user['_id'])
            return stream(f'data/{filetype}/{file}')
        return send_file(f'data/{filetype}/{file}')
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


@app.route('/service-worker.js')
def sendWorker():
    return flask.send_file('static/js/pwa/service-worker.js')


@app.route('/licence')
def licence():
    return send_file('LICENSE')


@app.route('/download')
def downloadApp():
    return send_file('mobile-app/app/release/app-release.apk')


@app.route('/terms')
def termsAndConditions():
    return render_template('terms_and_conditions.html')


@app.route('/cgu')
def CGU():
    return render_template('cgu.html')


if __name__ == '__main__':
    debug = False
    port = int(configuration['App']['port'])
    if '--debug' in sys.argv:
        debug = True
    if '--secure' in sys.argv:
        app.run(debug=debug, threaded=True, host='0.0.0.0', port=port, ssl_context=('certificate.pem', 'privatekey.pem'))
    else:
        app.run(debug=debug, threaded=True, host='0.0.0.0', port=port)
