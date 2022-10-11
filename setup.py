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
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.secret_key = "don't tell anyone"
api = Api(app)

# setting up database credentials
if ENV == 'dev':
    config = open('configlocal.txt', 'r').read()
    app.debug = True
elif ENV == 'prod':
    try:
        config = open('configprod.txt', 'r').read()
    except FileNotFoundError:
        print("Database config not found. Please provide necessary details.\nDatabase url:")
        db_url = input()
        print("Name of database:")
        db_name = input()
        print("Database username:")
        db_username = input()
        print("Database password:")
        db_password = input()
        with open('configprod.txt', 'w') as f:
            f.write('postgresql://{}:{}@{}/{}'.format(
                db_username, db_password, db_url, db_name))
        config = open('configprod.txt', 'r').read()
    app.debug = False
app.config['SQLALCHEMY_DATABASE_URI'] = config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


def open_config_from_file(fname, config_name):
    try:
        config = open(fname, 'r').read()
    except FileNotFoundError:
        print("{} config not found. Please provide necessary details.\n{}:".format(config_name, config_name))
        with open(fname, 'w') as f:
            f.write(input())
        config = open(fname, 'r').read()
    return config


facebook_app_id = open_config_from_file('facebook_app_id.txt', 'Facebook oauth app id')
facebook_app_secret = open_config_from_file('facebook_app_secret.txt', 'Facebook oauth app secret')
pixelyear_email_address = open_config_from_file('pixelyear_email.txt', 'Pixelyear email address')
email_password = open_config_from_file('email_password.txt', 'Pixelyear email account password')
db = SQLAlchemy(app)


# enum for more error-proof code
class Category(Enum):
    rate, anxiety, mood, weather, exercises, reading, health = range(7)
