from orm_objects import *
from flask import request, Response
import json
from exceptions import *
import jwt
from setup import jwt_key, Category
from math import ceil
from flask_restful import Resource
from uuid import uuid4
from bcrypt import hashpw, gensalt, checkpw


#   converts string to boolean, used in arguments parsing
def is_str_true(string):
    if str(string).lower() == "true" or string is True:
        return True
    return False


#   check whether given year is a leap year
def is_leap_year(year):
    year = int(year)
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 == 0:
        return True
    else:
        return False


#   creates an empty (all ratings are equal to 0) pixels data in the database
#   for a given category, user and year (current year by default),
#   optionally it can also fill the pixels data with desired ratings
def create_pixels(
        category, user_id, year=datetime.now().year, ratings=None):
    if ratings is None:
        #   creates an empty array of ratings
        if is_leap_year(year):
            r = [0] * 366
        else:
            r = [0] * 365
        ratings = ','.join(str(x) for x in r)
    new_pixels = Pixels(category, year, user_id, ratings)
    return new_pixels


#   converts index of year-to-string format to a datetime object for the
#   rating's day
def get_date_from_index(index, year):
    return datetime(int(year), 1, 1) + timedelta(index)


#   reverse of get_date_from_index function
def get_index_from_date(date):
    date_first_jan = datetime.strptime(
        "{}-1-1".format(date.year), "%Y-%m-%d")
    delta = date - date_first_jan
    pos = delta.days
    return pos


#   takes an array of ratings and deletes all of the empty (with 0 as a rate)
#   days from it
def get_nonzero_ratings(ratings):
    nonzero_ratings = []
    for rate in ratings:
        rate = int(rate)
        if rate != 0:
            nonzero_ratings.append(int(rate))
    return nonzero_ratings


#   takes 2 arrays of ratings and deletes the days where one of the arrays
#   is empty from both of them, needed for optimalization sake,
#   used in statistics,
#   it is used in circumstances where both arrays are from the same year,
#   either way it might now work because of the leap year
def get_nonzero_ratings_for_both(ratings1, ratings2, category1, category2):
    nonzero_ratings = []
    for rate1, rate2 in zip(ratings1, ratings2):
        rate1 = int(rate1)
        rate2 = int(rate2)
        if rate1 != 0 and rate2 != 0:
            nonzero_ratings.append({
                category1: rate1,
                category2: rate2})
    return nonzero_ratings


#   parses the arguments from json body of a request,
#   checks whether all of the necessary arguments are present
#   and if not it returns corresponding response
def parse_args_from_body(*args):
    try:
        args_table = []
        for arg in args:
            args_table.append(request.json[str(arg)])
        response = Response(
            json.dumps({
                "success": "OK."}),
            status=200, mimetype='application/json')
#   KeyError happens when arg is not found in request.json
    except KeyError:
        args_table = list(args)
        response = Response(
            json.dumps({"error": """One or more neccessary \
values not provided in request body!"""}),
            status=400, mimetype='application/json')
    return response, args_table


#   uses parse_args_from_body to parse arguments from json body
#   and also checks if the'yre not empty
def check_if_values_are_empty(*args):
    response, args_table = parse_args_from_body(*args)
    if response.status == "200 OK":
        for value in args_table:
            if value is None or value == "":
                response = Response(
                    json.dumps({
                        "error": "One or more fields are empty."}),
                    status=400, mimetype='application/json')
                break
    result_tuple = tuple([response] + args_table)
    return result_tuple


#   checks jwt of a given request provided in Authorization Token Bearer
#   and returns user_id of the token's owner
def verify_jwt(token=None):
    user_id = None
    try:
        if token is None:
            token = request.headers.get('Authorization')
        if token is None or token == "":
            response = Response(
                json.dumps(
                    {"error": "No token found in Authorization header."}),
                status=400, mimetype='application/json')
        else:
            token = token.replace("Bearer ", "")
            token = jwt.decode(token, jwt_key, 'HS256')
            uuid = token['uuid']
            user = User.query.filter_by(uuid=uuid).first()
            expiration_date = datetime.strptime(
                token['expiration_date'], "%Y-%m-%d %H:%M:%S.%f")
            creation_date = datetime.strptime(
                token['creation_date'], "%Y-%m-%d %H:%M:%S.%f")
            acceptable_creation_date = datetime.strptime(
                user.acceptable_token_creation_date, "%Y-%m-%d %H:%M:%S.%f")
            if expiration_date < datetime.today() or \
                    creation_date < acceptable_creation_date:
                raise WrongDateError
            if user is not None:
                user_id = user.user_id
                response = Response(
                        json.dumps({
                            "success": "Signature verification succeded."}),
                        status=200, mimetype='application/json')
            else:
                response = Response(
                        json.dumps({
                            "error": "User not found."}),
                        status=400, mimetype='application/json')
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError,
            AttributeError):
        response = Response(
                json.dumps({"error": "Signature verification failed."}),
                status=401, mimetype='application/json')
    except WrongDateError:
        response = Response(
            json.dumps({"error": "The token has expired!"}),
            status=401, mimetype='application/json')
    return response, user_id


#   combines check_if_values_are_empty and verify_jwt into one function,
#   useful for the sake of DRY and code readability
#   it returns values from checked arguments and user_id, also a response
#   object that states whether the operation was succesfull
def verify_jwt_and_check_for_empty(*args):
    """
        Returns a tuple:
        (reponse, user_id, request.json[arg1], request.json[arg2], ...).
    """
    response, user_id = verify_jwt()
    if response.status == "200 OK":
        args_table = []
        for index, result in enumerate(check_if_values_are_empty(*args)):
            if index == 0:
                response = result
            else:
                args_table.append(result)
    else:
        args_table = list(args)
    result_tuple = (response, user_id) + tuple(args_table)
    return result_tuple


#   returns a mean of ratings for a given user's year and category,
#   dominanta for exercises and reading and arithmethic mean for the
#   rest, returns 0 if ratings are empty
def get_mean(user_id, year, category):
    pixels = Pixels.query.filter_by(
        user_id=user_id, year=year, category=category).first()
    ratings = pixels.ratings.split(",")
    nonzero_ratings = get_nonzero_ratings(ratings)
    if nonzero_ratings == []:
        mean = 0
    elif category != "exercises" and category != "weather" \
            and category != "reading":
        mean = sum(nonzero_ratings)/len(nonzero_ratings)
        mean = round(mean, 2)
    else:
        ones = 0
        twos = 0
        threes = 0
        fours = 0
        fives = 0
        sixes = 0
        for rates in nonzero_ratings:
            for rate in str(rates):
                rate = int(rate)
                if rate == 1:
                    ones += 1
                elif rate == 2:
                    twos += 1
                elif rate == 3:
                    threes += 1
                elif rate == 4:
                    fours += 1
                elif rate == 5:
                    fives += 1
                elif rate == 6:
                    sixes += 1
        rates_counts = {
            '1': ones,
            '2': twos,
            '3': threes,
            '4': fours,
            '5': fives,
            '6': sixes}
        mean = int(max(rates_counts, key=rates_counts.get))
    return mean


#   changes acceptable_token_creation_date for a given user,
#   practically it works as a logout on all of the logged in
#   devices
def change_acceptable_token_creation_date(user_id=None, uuid=None):
    if user_id is not None:
        user = User.query.filter_by(user_id=user_id).first()
    if uuid is not None:
        user = User.query.filter_by(uuid=uuid).first()
    user.acceptable_token_creation_date = str(datetime.today())
    db.session.add(user)
    db.session.commit()


#   returns data of a worst or best day (stated as an argument),
#   for a given user in a given year,
#   can return combined data for both worst and best day,
#   used in statistics
def best_or_worst_day(ratings_array, year, best_or_worst):
    pixels_rate = ratings_array["rate"]
    pixels_anxiety = ratings_array["anxiety"]
    pixels_mood = ratings_array["mood"]
    pixels_weather = ratings_array["weather"]
    pixels_exercises = ratings_array["exercises"]
    pixels_reading = ratings_array["reading"]
    pixels_health = ratings_array["health"]
    old_pixels_zipped = list(zip(
        pixels_rate, pixels_anxiety, pixels_mood, pixels_weather,
        pixels_exercises, pixels_reading, pixels_health))
    pixels_zipped = []
    for pixel in old_pixels_zipped:
        if int(pixel[0]) != 0 and int(pixel[1]) != 0 and int(pixel[6]) != 0:
            pixels_zipped.append(pixel)
    if best_or_worst == "best":
        best_or_worst_day_values = (
            max(pixels_zipped,
                key=lambda s: int(s[0])-int(s[1])+int(s[2])+int(s[6])))
    elif best_or_worst == "worst":
        best_or_worst_day_values = (
            min(pixels_zipped,
                key=lambda s: int(s[0])-int(s[1])+int(s[2])+int(s[6])))
    elif best_or_worst == "best_and_worst":
        best_day_values = (
            max(pixels_zipped,
                key=lambda s: int(s[0])-int(s[1])+int(s[2])+int(s[6])))
        worst_day_values = (
            min(pixels_zipped,
                key=lambda s: int(s[0])-int(s[1])+int(s[2])+int(s[6])))
        best_day_index = old_pixels_zipped.index(best_day_values)
        worst_day_index = old_pixels_zipped.index(worst_day_values)
        best_day_date = get_date_from_index(
            best_day_index, year)
        worst_day_date = get_date_from_index(
            worst_day_index, year)
        return old_pixels_zipped, best_day_index, best_day_date,\
            worst_day_index, worst_day_date

    best_or_worst_day_index = old_pixels_zipped.index(best_or_worst_day_values)
    best_or_worst_day_date = get_date_from_index(
            best_or_worst_day_index, year)
    return old_pixels_zipped, best_or_worst_day_index, best_or_worst_day_date


#   transform exercises ratings data, replacing
#   the ratings with proper weights,
#   used in calculating correlations for statistics endpoints
def transform_exercises_data(comparable_data):
    for data in comparable_data:
        exercises = Category.exercises.name
        exercises_count = len(str(data[exercises]))
        if exercises_count < 3:
            data[exercises] = 1
        elif exercises_count >= 3 and exercises_count < 5:
            data[exercises] = 2
        elif exercises_count >= 5:
            data[exercises] = 3
    return comparable_data


#   takes 2 pixels ORM objects and returns their
#   ratings data in a format that allows for correlation
#   checkings, so it only accounts for the days where
#   ratings were filled for both checked categories
def get_comparable_data(pixels1, pixels2):
    if pixels1.category == pixels2.category:
        raise SameCategoriesException
    comparable_data = get_nonzero_ratings_for_both(
        pixels1.ratings.split(","), pixels2.ratings.split(","),
        pixels1.category, pixels2.category)
    if pixels1.category == "exercises" \
            or pixels2.category == "exercises":
        comparable_data = transform_exercises_data(comparable_data)
    return comparable_data


def get_interval(x, y):
    return list(range(x, y+1))


#   returns whether datas of ratings from 2 categories
#   correlate or not, using custom algorithm based on weights
#   max1 and max2 arguments are to be provided as arguments
#   for the optimalization and code readability sakes,
#   by default it checks if ratings for 2 categories
#   are both high for the day, with reverse=True it checks
#   if they're both low
def correlation(max1, max2, comparable_datas, reverse=False):
    category1 = list(comparable_datas[0].keys())[0]
    category2 = list(comparable_datas[0].keys())[1]
    low = get_interval(1, ceil(max1/3))
    medium = get_interval(ceil(max1/3)+1, ceil(2*max1/3))
    high = get_interval(ceil(2*max1/3)+1, 9999)
    if reverse is True:
        low2 = get_interval(1, ceil(max2/3))
        medium2 = get_interval(ceil(max2/3)+1, ceil(2*max2/3))
        high2 = get_interval(ceil(2*max2/3)+1, 9999)
    else:
        high2 = get_interval(1, ceil(max2/3))
        medium2 = get_interval(ceil(max2/3)+1, ceil(2*max2/3))
        low2 = get_interval(ceil(2*max2/3)+1, 9999)
    correlations = 0
    for data in comparable_datas:
        if data[category1] in low and data[category2] in low2:
            correlations += 1
            continue
        elif data[category1] in medium and data[category2] in medium2:
            correlations += 1
            continue
        elif data[category1] in high and data[category2] in high2:
            correlations += 1
    if len(comparable_datas) != 0 and \
            correlations/len(comparable_datas) >= 0.5:
        return True
    return False


#   logins the user using jwt
def login_user(email, password, never_expire, oauth=False):
    user = User.query.filter_by(email=email).first()
    if user is None:
        response = Response(
            json.dumps({"error": "User not found!"}),
            status=400, mimetype='application/json')
    elif (oauth is True and user.oauth_user is True) or checkpw(
            password.encode("utf-8"), user.password.encode("utf-8")):
        if never_expire is True:
            expiration_date = str(datetime.today() + timedelta(
                days=9999))
        else:
            expiration_date = str(datetime.today() + timedelta(
                hours=12))
        TOKEN = jwt.encode({'uuid': user.uuid,
                            'creation_date': str(datetime.today()),
                            'expiration_date': expiration_date
                            }, jwt_key)
        response = Response(
            json.dumps({'token': TOKEN,
                        'uuid': user.uuid,
                        'email': email}),
            status=202, mimetype='application/json')
    elif oauth is False and user.oauth_user is True:
        response = Response(
            json.dumps({"error": "You need to login via facebook!"}),
            status=400,
            mimetype='application/json')
    else:
        response = Response(
            json.dumps({"error": "Wrong password!"}), status=400,
            mimetype='application/json')
    return response


#   registers the user
def register_user(email, password, repassword, oauth=False):
    try:
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
            password = hashpw(
                password.encode("utf-8"),
                gensalt(14)).decode("utf-8")
            user_uuid = uuid4()
            new_user = User(user_uuid, email, password,
                            "", "", "", oauth)
            db.session.add(new_user)
            db.session.commit()
            new_user_id = new_user.user_id
            for category in Category:
                category = category.name
                created_pixels = create_pixels(
                    category, new_user_id)
                db.session.add(created_pixels)
            db.session.commit()
            response = Response(
                json.dumps({"success": "Successfuly created account."}),
                status=201, mimetype='application/json')
    except InvalidEmailException:
        response = Response(
                json.dumps({"error": "Invalid email."}),
                status=400, mimetype='application/json')
    return response
