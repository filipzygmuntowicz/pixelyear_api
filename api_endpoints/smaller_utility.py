from functions import *


class YearsWithActivePixel(Resource):
    #   returns years where the user has rated atleast one day
    def get(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            pixels = Pixels.query.filter_by(
                        user_id=user_id).all()
            years = []
            for pixel in pixels:
                if pixel.year not in years:
                    years.append(int(pixel.year))
            years.sort(reverse=True)
            response = Response(
                    json.dumps({
                        'years': years}),
                    status=200, mimetype='application/json')
        return response


class UpdatedToday(Resource):
    #   returns the categories that the user has rated today with their
    #   corresponding rates, also returns unrated categories
    #   in a seperate array, allows for the returning data's categories to be
    #   in numeric format with ?type=numeric argument
    def get(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            today = datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0)
            date_first_jan = datetime.strptime(
                "{}-1-1".format(today.year), "%Y-%m-%d")
            delta = today - date_first_jan
            pos = delta.days
            response_json = {"updated": {}, "not_updated": []}
            for category in Category:
                today_pixel_rate = Pixels.query.filter_by(
                    user_id=user_id, category=category.name,
                    year=today.year).first().ratings
                today_pixel_rate = today_pixel_rate.split(",")
                args = request.args
                if "type" in args and "numeric" in args["type"]:
                    category = str(category.value)
                else:
                    category = category.name
                if today_pixel_rate[pos] == "0":
                    response_json["not_updated"].append(category)
                else:
                    response_json["updated"][str(category)] = today_pixel_rate[
                        pos]
            response = Response(
                        json.dumps(response_json),
                        status=200, mimetype='application/json')
        return response


class UpdatedTodayCategory(Resource):
    #   same as Updated_today but for a single category provided in url
    def get(self, category):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            today = datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0)
            date_first_jan = datetime.strptime(
                "{}-1-1".format(today.year), "%Y-%m-%d")
            delta = today - date_first_jan
            pos = delta.days
            if category == "all":
                response_json = {"updated": {}, "not_updated": []}
                for category in Category:
                    today_pixel_rate = Pixels.query.filter_by(
                        user_id=user_id, category=category.name,
                        year=today.year).first().ratings
                    today_pixel_rate = today_pixel_rate.split(",")
                    args = request.args
                    if "type" in args and "numeric" in args["type"]:
                        category = str(category.value)
                    else:
                        category = category.name
                    if today_pixel_rate[pos] == "0":
                        response_json["not_updated"].append(category)
                    else:
                        response_json[
                            "updated"][str(category)] = today_pixel_rate[pos]
                response = Response(
                            json.dumps(response_json),
                            status=200, mimetype='application/json')
            else:
                today_pixel_rate = Pixels.query.filter_by(
                    user_id=user_id, category=category,
                    year=today.year).first().ratings
                today_pixel_rate = today_pixel_rate.split(",")
                response_json = {"updated": {}, "not_updated": []}
                if today_pixel_rate[pos] == "0":
                    response_json["not_updated"].append(category)
                else:
                    response_json[
                        "updated"][str(category)] = today_pixel_rate[pos]
                response = Response(
                    json.dumps(response_json),
                    status=200, mimetype='application/json')
        return response


class DaysWithActiveJournal(Resource):
    #   returns in year-to-string format data
    #   for filled and unfilled journals
    def get(self, year):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            date_first = datetime.strptime(
                "{}-1-1".format(year), "%Y-%m-%d")
            date_last = datetime.strptime(
                "{}-12-31".format(year), "%Y-%m-%d")
            journals = Journal.query.filter_by(user_id=user_id).filter(
                Journal.date.between(date_first, date_last)).all()
            if is_leap_year(year):
                journal_days = [0] * 366
            else:
                journal_days = [0] * 365
            if journals is not None:
                for journal in journals:
                    journal_days[get_index_from_date(journal.date)] = 1
            journal_days = ','.join(str(x) for x in journal_days)
            response_json = {"journal_days": journal_days}
            response = Response(
                        json.dumps(response_json),
                        status=200, mimetype='application/json')
        return response
