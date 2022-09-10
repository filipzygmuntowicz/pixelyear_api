from functions import *
from uuid import uuid4
from bcrypt import hashpw, gensalt, checkpw


class Register(Resource):

    def post(self):
        try:
            response, email, password, repassword = check_if_values_are_empty(
                "email", "password", "repassword")
            if response.status == "200 OK":
                if "@" not in email or "." not in email:
                    raise InvalidEmailException
                user = User.query.filter_by(email=email).first()
                if user is not None:
                    response = Response(
                        json.dumps({"error": "Email alredy in use!"}),
                        status=400, mimetype='application/json')
                elif password != repassword:
                    response = Response(
                        json.dumps({"error": "Passwords do not match!"}),
                        status=400, mimetype='application/json')
                else:
                    last_user = User.query.order_by(
                        User.user_id.desc()).first()
                    new_user_id = 1
                    if last_user is not None:
                        new_user_id = last_user.user_id + 1
                    password = hashpw(
                        password.encode("utf-8"),
                        gensalt(14)).decode("utf-8")
                    user_uuid = uuid4()
                    new_user = User(user_uuid, email, password,
                                    "", "", "")
                    db.session.add(new_user)
                    for category in Category:
                        category = category.name
                        category_object = create_pixels(
                            category, new_user_id)
                        db.session.add(category_object)
                    db.session.commit()
                    response = Response(
                        json.dumps({"success": "Succesfuly created account."}),
                        status=201, mimetype='application/json')
        except InvalidEmailException:
            response = Response(
                    json.dumps({"error": "Invalid email."}),
                    status=400, mimetype='application/json')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept')
        return response


class Logging(Resource):

    def post(self):
        response, email, password = check_if_values_are_empty(
            "email", "password")
        try:
            never_expire = is_str_true(request.json['never_expire'])
        except KeyError:
            never_expire = False
        if response.status == "200 OK":
            user = User.query.filter_by(email=email).first()
            if user is None:
                response = Response(
                    json.dumps({"error": "User not found!"}),
                    status=400, mimetype='application/json')
            elif checkpw(
                    password.encode("utf-8"), user.password.encode("utf-8")):
                if never_expire is True:
                    expiration_date = str(datetime.today() + timedelta(
                        days=9999))
                else:
                    expiration_date = str(datetime.today() + timedelta(
                        hours=1))
                TOKEN = jwt.encode({'uuid': user.uuid,
                                    'creation_date': str(datetime.today()),
                                    'expiration_date': expiration_date
                                    }, jwt_key)
                response = Response(
                    json.dumps({'token': TOKEN,
                                'uuid': user.uuid,
                                'email': email}),
                    status=202, mimetype='application/json')
            else:
                response = Response(
                    json.dumps({"error": "Wrong password!"}), status=400,
                    mimetype='application/json')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept')
        return response


class Create_password_reset_token(Resource):

    def post(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            user = User.query.filter_by(user_id=user_id).first()
            password_reset_token = jwt.encode({
                'is_password_reset_token': True,
                'uuid': user.uuid,
                'creation_date': str(datetime.today()),
                'expiration_date': str(datetime.today() + timedelta(hours=0.5))
                }, jwt_key)
            response = Response(
                    json.dumps({"succes": """
Password reset link was sent to {}!
 https://127.0.0.1:5000/api/reset_password/{}""".format(
                        user.email, password_reset_token)}),
                    status=400, mimetype='application/json')
        return response


class Reset_password(Resource):

    def post(self, password_reset_token):
        password_reset_token = password_reset_token.replace("Bearer ", "")
        try:
            token = jwt.decode(password_reset_token, jwt_key, 'HS256')
            is_password_reset_token = token['is_password_reset_token']
            if is_password_reset_token is not True:
                raise WrongTokenException
            response, user_id = verify_jwt(password_reset_token)
            if response.status == "200 OK":
                response, password, repassword = check_if_values_are_empty(
                    "password", "repassword")
                if response.status == "200 OK":
                    if password != repassword:
                        raise ValuesDoNotMatchException
                    user = User.query.filter_by(user_id=user_id).first()
                    new_password = hashpw(
                        password.encode("utf-8"),
                        gensalt(14)).decode("utf-8")
                    user.password = new_password
                    db.session.add(user)
                    db.session.commit()
                    change_acceptable_token_creation_date(user_id)
                    response = Response(
                        json.dumps({"succes": "Succesfuly changed password!"}),
                        status=200, mimetype='application/json')
        except (WrongTokenException, KeyError):
            response = Response(
                            json.dumps({"error": "Wrong password reset url!"}),
                            status=400, mimetype='application/json')
        except ValuesDoNotMatchException:
            response = Response(
                            json.dumps({"error": "Passwords do not match!"}),
                            status=400, mimetype='application/json')
        return response


class Clear_logged_sessions(Resource):

    def patch(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            change_acceptable_token_creation_date(user_id)
            response = Response(
                json.dumps({
                    "succes": "Succesfuly cleared logged in sessions."
                    }),
                status=200, mimetype='application/json')
        return response
