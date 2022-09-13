from functions import *


class Main(Resource):
    #   returns pixels data
    def get(self, year, category):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            pixels = Pixels.query.filter_by(
                user_id=user_id, year=year, category=category).first()
        #   creates ratings array out of string from database
            ratings = pixels.ratings.split(",")
            if len(ratings) == 366:
                return_pixels = {
                    "january": ratings[0:31],
                    "february": ratings[31:60],
                    "march": ratings[60:91],
                    "april": ratings[91:121],
                    "may": ratings[121:152],
                    "june": ratings[152:182],
                    "july": ratings[182:213],
                    "august": ratings[213:244],
                    "september": ratings[244:274],
                    "october": ratings[274:305],
                    "november": ratings[305:335],
                    "december": ratings[335:367]
                }
            else:
                return_pixels = {
                    "january": ratings[0:31],
                    "february": ratings[31:59],
                    "march": ratings[59:90],
                    "april": ratings[90:120],
                    "may": ratings[120:151],
                    "june": ratings[151:181],
                    "july": ratings[181:212],
                    "august": ratings[212:243],
                    "september": ratings[243:273],
                    "october": ratings[273:304],
                    "november": ratings[304:334],
                    "december": ratings[334:366]
                }
        #   different format for "exercises" category
            if category != Category.exercises.name:
                for month in return_pixels:
                    return_pixels[month] = ''.join(
                        str(pixels_month) for pixels_month in return_pixels[
                            month])
            response = Response(
                        json.dumps(return_pixels),
                        status=200, mimetype='application/json')
        return response

    #   changes values of pixels ratings
    def patch(self, year, category):
        response, user_id, new_pixel_values, date_pixel = \
            verify_jwt_and_check_for_empty("pixel_values", "date")
        if response.status == "200 OK":
            try:
                date_pixel = datetime.strptime(date_pixel, "%Y-%m-%d")
                if str(date_pixel.year) != str(year):
                    raise ValuesDoNotMatchException
                #   user can't edit future pixels
                if date_pixel > datetime.today().replace(
                        hour=23, minute=59, second=59):
                    raise WrongDateError
                if category == Category.rate.name or \
                        category == Category.mood.name:
                    max_rating = 5
                elif category == Category.anxiety.name or \
                        category == Category.health.name:
                    max_rating = 4
                elif category == Category.exercises.reading:
                    max_rating = 99999
                elif category == Category.weather.name or\
                        category == Category.exercises.name:
                    max_rating = 6
                else:
                    raise InvalidCategoryError
                values_checked = []
                #   reading doesn't really have a max_rating and
                #   exercises rate data is not parsed yet
                if category != Category.exercises.name and \
                        category != Category.reading.name and int(
                            new_pixel_values) > max_rating:
                    raise InvalidNewPixelValues
                #   parsing exercises ratings data and checking if it's correct
                if category == "exercises":
                    if ("1" in str(new_pixel_values) and
                            str(new_pixel_values) != "1"):
                        raise InvalidCategoryError
                    for value in str(new_pixel_values):
                        value = int(value)
                        if value < 0 or value > max_rating or \
                                value in values_checked:
                            raise InvalidNewPixelValues
                        values_checked.append(value)
                    values_checked.sort()
                    new_pixel_values = ''.join(
                        str(value) for value in values_checked)
                pixels = Pixels.query.filter_by(
                    user_id=user_id, year=year, category=category).first()
                #   allows to patch non-existing yet pixels, since the process
                #   of adding new empty pixels is a bit tricky
                if pixels is None:
                    zero_pixels = create_pixels(category, user_id, year)
                    db.session.add(zero_pixels)
                    db.session.commit()
                    pixels = Pixels.query.filter_by(
                        user_id=user_id, year=year, category=category).first()
                ratings = pixels.ratings.split(",")
                date_first_jan = datetime.strptime(
                    "{}-1-1".format(date_pixel.year), "%Y-%m-%d")
                delta = date_pixel - date_first_jan
                pos = delta.days
                ratings[pos] = new_pixel_values
                ratings = ','.join(
                            str(pixel_rating) for pixel_rating in ratings)
                pixels.ratings = ratings
                db.session.add(pixels)
                db.session.commit()
                response = Response(
                        json.dumps(
                            {"succes": """Succesfuly changed values \
of pixel {} to {}""".format(pos+1,
                             new_pixel_values)}), status=200,
                        mimetype='application/json')
            except ValueError:
                response = Response(
                    json.dumps({"error": "date in invalid format."}),
                    status=400, mimetype='application/json')
            except InvalidCategoryError:
                response = Response(
                    json.dumps({"error": "Invalid category."}),
                    status=400, mimetype='application/json')
            except InvalidNewPixelValues:
                response = Response(
                    json.dumps({"error": "Invalid pixel values."}),
                    status=400, mimetype='application/json')
            except WrongDateError:
                response = Response(
                    json.dumps({"error": "You can't edit the future pixels!"}),
                    status=400, mimetype='application/json')
            except ValuesDoNotMatchException:
                response = Response(
                    json.dumps({"error": """
Two different years provided in url and request's body!"""}),
                    status=400, mimetype='application/json')
        return response
