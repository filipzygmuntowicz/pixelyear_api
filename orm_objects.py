from setup import db
from datetime import datetime, timedelta


class User(db.Model):

    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    phone = db.Column(db.String)
    avatar = db.Column(db.String)
    ips = db.Column(db.String)
    registration_date = db.Column(db.String)
    acceptable_token_creation_date = db.Column(db.String)

    def __init__(
        self, user_id, uuid, email, password,
        phone, avatar, ips
    ):
        self.user_id = user_id
        self.uuid = uuid
        self.email = email
        self.password = password
        self.phone = phone
        self.avatar = avatar
        self.ips = ips
        self.registration_date = str(datetime.today())
        self.acceptable_token_creation_date = str(datetime.today())


class Pixels(db.Model):

    __tablename__ = 'Pixels'
    pixels_id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String)
    year = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('User'))
    user = db.relationship(
        "User", backref=db.backref("user_pixels", uselist=False))
    ratings = db.Column(db.String)

    def __init__(
        self, pixels_id, category, year, user_id, ratings
    ):
        self.pixels_id = pixels_id
        self.category = category
        self.year = year
        self.user_id = user_id
        self.ratings = ratings
