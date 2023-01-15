from flask import Flask
import routes as trickstok

if __name__ == '__main__':
    app = Flask('Tricks Tok, The TikTok of Tricks')
    trickstok.run(app)



