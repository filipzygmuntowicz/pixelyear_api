from setup import db
from datetime import datetime, timedelta


#   table for users, ips for potential future user's ip addresses storage, 
#   acceptable_token_creation_date states how old is the oldest acceptable jwt
#   token for logging in
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
    oauth_user = db.Column(db.Boolean)

    def __init__(
        self, uuid, email, password,
        phone, avatar, ips, oauth_user
    ):
        self.uuid = uuid
        self.email = email
        self.password = password
        self.phone = phone
        self.avatar = avatar
        self.ips = ips
        self.registration_date = str(datetime.today())
        self.acceptable_token_creation_date = str(datetime.today())
        self.oauth_user = oauth_user


#   table for all pixels related data, core of the app
#   one row stores data of user's ratings for one year,
#   the ratings data is stored as a string in
#   format: "r,r,r,...,r" (called year-to-string format in documentation)
#   where r is a rating for a given day, so there is either
#   365 or 366 ratings in a given row and first r is for the 1st of january
#   and last is for the 31st december of a given year,
#   an empty (not filled by user) day always has rating equal to 0
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
        self, category, year, user_id, ratings
    ):
        self.category = category
        self.year = year
        self.user_id = user_id
        self.ratings = ratings


#   table for journals
class Journal(db.Model):

    __tablename__ = 'Journal'
    entry_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('User'))
    user = db.relationship(
        "User", backref=db.backref("user_journal", uselist=False))
    date = db.Column(db.DateTime)

    def __init__(
        self, content, user_id, date
    ):
        self.content = content
        self.user_id = user_id
        self.date = date
