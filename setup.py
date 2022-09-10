from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from enum import Enum


jwt_key = 'placeholder'
ENV = 'prod'
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "don't tell anyone"
api = Api(app)


if ENV == 'dev':
    config = open('configlocal.txt', 'r').read()
    app.debug = True
elif ENV == 'prod':
    config = open('configheroku.txt', 'r').read()
    app.debug = False

app.config['SQLALCHEMY_DATABASE_URI'] = config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

db = SQLAlchemy(app)


# Enum for more error-proof code
class Category(Enum):
    rate, anxiety, mood, weather, exercises, reading, health = range(7)
