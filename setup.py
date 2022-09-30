from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from enum import Enum
from os import path, getcwd

# globals
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
AVATARS_FOLDER = path.join(getcwd(), "avatars")
jwt_key = 'placeholder'
ENV = 'prod'
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['AVATARS_FOLDER'] = AVATARS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.secret_key = "don't tell anyone"
api = Api(app)

# setting up database credentials
if ENV == 'dev':
    config = open('configlocal.txt', 'r').read()
    app.debug = True
elif ENV == 'prod':
    config = open('configheroku.txt', 'r').read()
    app.debug = False

app.config['SQLALCHEMY_DATABASE_URI'] = config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
facebook_app_id = open('facebook_app_id.txt', 'r').read()
facebook_app_secret = open('facebook_app_secret.txt', 'r').read()
email_password = open('email_password.txt', 'r').read()
db = SQLAlchemy(app)


# enum for more error-proof code
class Category(Enum):
    rate, anxiety, mood, weather, exercises, reading, health = range(7)
