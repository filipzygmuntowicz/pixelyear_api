from functions import *


class Years_with_active_pixel(Resource):

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


class Updated_today(Resource):

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


class Updated_today_category(Resource):

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
                response_json = {"updated": [], "not_updated": []}
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
                        response_json["updated"].append(category)
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
