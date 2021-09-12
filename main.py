import json
import random

import flask
import requests
from flask import Flask, request, redirect, render_template


def randomComment():
    name = requests.get('https://api.namefake.com/').json()['name']
    content = random.choice(random.choice(requests.get('https://poetrydb.org/poemcount/10/lines.json').json())['lines'])
    time = random.choice(['Maintenant', f'Il y a {random.choice([1, 2, 3, 4, 5, 6, 7, 8])}h', f'Il y a {random.choice([1, 2, 3, 4, 5, 6, 7, 8])}jours'])
    pp = requests.post(
        "https://api.deepai.org/api/text2img",
        data={
            'text': name,
        },
        headers={'api-key': 'd6ffa577-9556-4947-a2fe-e25e0c87bc04'}
    ).json()["output_url"]
    return {
        "userName": name,
        "timePosted": time,
        "profilePhoto":
            pp,
        "comment": content
    }


app = Flask('TrickyTricks, The TikTok of Tricks')

videos_ = ['surf-kickflip.mp4', 'Clean%20kickflip.mp4', 'tramp.mp4', 'longboard.mp4', 'scooter.mp4', 'fabio.mp4', 'bmx.mp4']

videos = {'srcs': ['/static/assets/' + video for video in videos_], 'ids': [video for video in videos_]}

print([videos['srcs'][num]for num in range(4)])
print([videos['ids'][num] for num in range(4)])

comments = json.loads(open('static/test/comments.json').read())
# with open('static/test/comments.json', 'w+') as f:
#     f.write(json.dumps(comments))
#     print(f.read())
#     f.close()


def auth(returned):
    print(request.cookies)
    return returned


@app.route('/home')
def home():
    return auth(render_template('index.html', videos=videos))


@app.route('/service-worker.js')
def sendWorker():
    return flask.send_file('static/js/pwa/service-worker.js')


@app.route('/')
def form():
    return auth(render_template('connect.html'))


@app.route('/favicon.png')
def favicon():
    return flask.send_file('static/assets/trickstok_logo_trans.png')


@app.route('/get-comments/<video>')
def getComments(video):
    return auth(flask.jsonify(comments[video]))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
