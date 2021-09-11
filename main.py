import flask
from flask import Flask, request, redirect, render_template
import pymongo

app = Flask('TricksTok, The TikTok of Tricks')

comments = {
    "test": [
        {
            "userName": "CAMARM",
            "timePosted": "il y a 5h",
            "profilePhoto":
                "https://www.camarm.dev/favicon.png",
            "comment": "Waww so clean"
        },
        {
            "userName": "Tricktok official",
            "timePosted": "il y a 4h",
            "profilePhoto":
                "/favicon.png",
            "comment": "Too clean men, gg !"
        },
        {
            "userName": "Mr. Mopi",
            "timePosted": "il y a 2h",
            "profilePhoto":
                "https://6erxg60qvo1qvjha44jrgpan-wpengine.netdna-ssl.com/wp-content/uploads/2018/10/Mr-Billy-Urudra-President-MOPI.jpg",
            "comment": "Il m'en faut un c'est sûr !"
        },
        {
            "userName": "Tony Hawk",
            "timePosted": "Maintenant",
            "profilePhoto":
                "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Tony_Hawk_2016_%28cropped%29.jpg/260px-Tony_Hawk_2016_%28cropped%29.jpg",
            "comment": "Mieux que  moi !"
        },
    ]
}


videos = ['/static/assets/' + video for video in ['surf-kickflip.mp4', 'Clean%20kickflip.mp4', 'tramp.mp4', 'longboard.mp4', 'scooter.mp4', '']]


def auth(returned):
    print(request.cookies)
    return returned


@app.route('/home')
def home():
    return auth(render_template('index.html', videos=videos))


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
