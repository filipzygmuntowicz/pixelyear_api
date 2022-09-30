from functions import *
from requests import get
from os import listdir
from setup import app, path, facebook_app_id, facebook_app_secret,\
    ALLOWED_EXTENSIONS, email_password
from flask import send_file
from shutil import copyfileobj
from email.message import EmailMessage
import smtplib
import ssl


class Register(Resource):
    #   register procedure with a minimalistic email syntax check, the user
    #   gets assigned uuid and his password is stored hashed with bcrypt,
    #   also empty pixels data is created for him for the current year
    def post(self):
        response, email, password, repassword = check_if_values_are_empty(
            "email", "password", "repassword")
        if response.status == "200 OK":
            response = register_user(email, password, repassword)
        return response


class Logging(Resource):
    #   returns jwt token for the user if the credentials are correct,
    #   the token stores user's uuid, email, creation and expiration date
    #   and is used with every single request for user authenthication
    def post(self):
        response, email, password = check_if_values_are_empty(
            "email", "password")
        try:
            never_expire = is_str_true(request.json['never_expire'])
        except KeyError:
            never_expire = False
        if response.status == "200 OK":
            response = login_user(email, password, never_expire)
        return response


class CreatePasswordResetToken(Resource):
    #   creates the password reset token and sends
    #   the url (which uses the token) for password reset to the user's email
    def post(self):
        response, email = check_if_values_are_empty(
            "email")
        if response.status == "200 OK":
            response = Response(
                json.dumps({
                    "success": "Password reset link was sent to {}!".format(
                        email)}),
                status=200, mimetype='application/json')
            user = User.query.filter_by(email=email).first()
            if user is not None:
                password_reset_token = jwt.encode({
                    'is_password_reset_token': True,
                    'uuid': user.uuid,
                    'creation_date': str(datetime.today()),
                    'expiration_date': str(datetime.today() + timedelta(
                        hours=0.5))
                    }, jwt_key)
                email_sender = 'pixelyearapp@gmail.com'
                email_receiver = email
                subject = 'Pixelyear pasword reset link'
                if user.oauth_user is True:
                    body = """
Someone tried to reset password to your Pixelyear account but it's not possible to do that if you've registered via google or facebook.
""".format(password_reset_token)
                else:
                    body = """
Your password reset link:
localhost:3000/reset-password?token={}
""".format(password_reset_token)
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content(body)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                        'smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, email_receiver, em.as_string())
        return response


class ResetPassword(Resource):
    #   changes user's password to the one provided in request's json body
    def post(self):
        response, password, repassword, password_reset_token = \
            check_if_values_are_empty(
                "password", "repassword", "token")
        try:
            token = jwt.decode(password_reset_token, jwt_key, 'HS256')
            is_password_reset_token = token['is_password_reset_token']
            if is_password_reset_token is not True:
                raise WrongTokenException
            if response.status == "200 OK":
                if password != repassword:
                    raise ValuesDoNotMatchException
                user = User.query.filter_by(uuid=token["uuid"]).first()
                new_password = hashpw(
                    password.encode("utf-8"),
                    gensalt(14)).decode("utf-8")
                user.password = new_password
                db.session.add(user)
                db.session.commit()
                change_acceptable_token_creation_date(uuid=token["uuid"])
                response = Response(
                    json.dumps({"success": "Successfully changed password!"}),
                    status=200, mimetype='application/json')
        except (jwt.exceptions.InvalidSignatureError, WrongTokenException,
                jwt.exceptions.DecodeError, KeyError):
            response = Response(
                            json.dumps({"error": "Wrong password reset url!"}),
                            status=400, mimetype='application/json')
        except ValuesDoNotMatchException:
            response = Response(
                            json.dumps({"error": "Passwords do not match!"}),
                            status=400, mimetype='application/json')
        return response


class ClearLoggedSessions(Resource):
    #   makes all of the jwt tokens made by user obsolete effectively
    #   logging off the user everywhere
    def patch(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            change_acceptable_token_creation_date(user_id)
            response = Response(
                json.dumps({
                    "success": "Successfully cleared logged in sessions."
                    }),
                status=200, mimetype='application/json')
        return response


class UploadAvatar(Resource):
    #   changes user's avatar the one given in form-data body
    def patch(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            try:
                if 'avatar' not in request.files:
                    print("No avatar key")
                    raise InvalidAvatarException
                file = request.files['avatar']
                filename = file.filename
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                if '.' not in filename or \
                        file_extension not in ALLOWED_EXTENSIONS:
                    print("Bad exception")
                    raise InvalidAvatarException
                user = User.query.filter_by(user_id=user_id).first()
                file.save(path.join(
                    app.config['AVATARS_FOLDER'],
                    str(user.uuid) + "." + file_extension))
                response = Response(
                    json.dumps({
                        "succes": "Successfully uploaded avatar."
                        }),
                    status=200, mimetype='application/json')
            except InvalidAvatarException:
                response = Response(
                    json.dumps({
                        "error": "Invalid avatar file."
                        }),
                    status=400, mimetype='application/json')
        return response


class DownloadAvatar(Resource):
    # returns avatar of user with given uuid
    def get(self, uuid):
        filepath = path.join(app.config['AVATARS_FOLDER'], "default.png")
        for file in listdir((app.config['AVATARS_FOLDER'])):
            if uuid in file:
                filepath = path.join(app.config['AVATARS_FOLDER'], file)
                break
        return send_file(filepath, mimetype='image/gif')


class DeleteAccount(Resource):
    #   deletes user's account
    def delete(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            user = User.query.filter_by(user_id=user_id).first()
            email = user.email
            Journal.query.filter_by(user_id=user_id).delete()
            Pixels.query.filter_by(user_id=user_id).delete()
            User.query.filter_by(email=email).delete()
            response = Response(
                json.dumps({
                    "success": "Successfully deleted account."
                    }),
                status=200, mimetype='application/json')
            db.session.commit()
        return response


class FacebookLogin(Resource):
    #   gets user's email and profile picture from facebook graph api and uses
    #   them to log the user in, registers the user if he's not yet registered
    def post(self):
        response, code, state = check_if_values_are_empty("code", "state")
        if response.status == "200 OK":
            #   https://www.facebook.com/v15.0/dialog/oauth?client_id=583211373601189&redirect_uri=https://localhost:3000/oauth&state=huj
            oauth_redirect = "https://localhost:3000/oauth"
            request = get("https://graph.facebook.com/v15.0/oauth/access_token?client_id={}&redirect_uri={}&client_secret={}&code={}".format(facebook_app_id, oauth_redirect, facebook_app_secret, code))
            facebook_response = dict(request.json())
            facebook_response["state"] = state
            try:
                token = facebook_response["access_token"]
                user_data_response = get("https://graph.facebook.com/v15.0/me?fields=email,picture&access_token={}".format(token)).json()
                email = user_data_response["email"]
                print(user_data_response)
                user = User.query.filter_by(email=email).first()
                if user is None:
                    register_user(
                        email=email, password="", repassword="", oauth=True)
                    if user_data_response['picture']['data']['url'] != "https://scontent-waw1-1.xx.fbcdn.net/v/t1.30497-1/84628273_176159830277856_972693363922829312_n.jpg?stp=c15.0.50.50a_cp0_dst-jpg_p50x50&_nc_cat=1&ccb=1-7&_nc_sid=12b3be&_nc_ohc=FvDXNTGwVu8AX-2zO0Q&_nc_ht=scontent-waw1-1.xx&edm=AP4hL3IEAAAA&oh=00_AT_mU_RedRbpY_O6EWbjMl_ZZz7UCwcuUcv77wWpnOzAuQ&oe=635ABD19":
                        user = User.query.filter_by(email=email).first()
                        uuid = user.uuid
                        r = get(user_data_response['picture']['data']['url'],
                                stream=True)
                        with open(path.join(
                                app.config['AVATARS_FOLDER'], uuid + ".png"),
                                    'wb') as file:
                            r.raw.decode_content = True
                            copyfileobj(r.raw, file)
                response = login_user(
                    email=email, password="oauth", never_expire=False, oauth=True)
            except KeyError:
                response = Response(
                    json.dumps({
                        "error": "Invalid facebook token."
                        }),
                    status=400, mimetype='application/json')
        return response


class GoogleLogin(Resource):
    #   gets user's email and profile picture from google api and uses
    #   them to log the user in, registers the user if he's not yet registered
    def post(self):
        response, token, state = check_if_values_are_empty("token", "state")
        if response.status == "200 OK":
            user_data_response = get("https://www.googleapis.com/oauth2/v3/userinfo?access_token={}".format(token)).json()
            print(user_data_response)
            try:
                email = user_data_response["email"]
                user = User.query.filter_by(email=email).first()
                if user is None:
                    register_user(
                        email=email, password="", repassword="", oauth=True)
                    if user_data_response['picture'] != "https://lh3.googleusercontent.com/a/default-user=s96-c":
                        user = User.query.filter_by(email=email).first()
                        uuid = user.uuid
                        r = get(user_data_response['picture'], stream=True)
                        with open(path.join(
                                app.config['AVATARS_FOLDER'], uuid + ".png"),
                                    'wb') as file:
                            r.raw.decode_content = True
                            copyfileobj(r.raw, file)
                response = login_user(
                    email=email, password="oauth", never_expire=False, oauth=True)
            except KeyError:
                response = Response(
                    json.dumps({
                        "error": "Invalid google token."
                        }),
                    status=400, mimetype='application/json')
        return response
