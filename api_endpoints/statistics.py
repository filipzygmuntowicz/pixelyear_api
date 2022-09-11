from functions import *


class Mean(Resource):

    def get(self, year):

        response, user_id = verify_jwt()
        if response.status == "200 OK":
            means = {}
            for category in Category:
                args = request.args
                if "type" in args and "numeric" in args["type"]:
                    category_key_name = str(category.value)
                else:
                    category_key_name = category.name
                means[category_key_name] = get_mean(
                    user_id, year, category.name)
            response = Response(
                json.dumps({'means': means}),
                status=200, mimetype='application/json')
        return response


class Mean_category(Resource):

    def get(self, year, category):

        response, user_id = verify_jwt()
        if response.status == "200 OK":
            if category != "all":
                mean = get_mean(user_id, year, category)
                response = Response(
                    json.dumps({'mean': mean}),
                    status=200, mimetype='application/json')
            else:
                means = {}
                for category in Category:
                    args = request.args
                    if "type" in args and "numeric" in args["type"]:
                        category_key_name = str(category.value)
                    else:
                        category_key_name = category.name
                    means[category_key_name] = get_mean(
                        user_id, year, category.name)
                response = Response(
                    json.dumps({'means': means}),
                    status=200, mimetype='application/json')
        return response


class Statistics(Resource):

    def get(self, year):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            pixels_rate = Pixels.query.filter_by(
                user_id=user_id, year=year, category="rate").first()
            pixels_anxiety = Pixels.query.filter_by(
                user_id=user_id, year=year, category="anxiety").first()
            pixels_mood = Pixels.query.filter_by(
                user_id=user_id, year=year, category="mood").first()
            pixels_weather = Pixels.query.filter_by(
                user_id=user_id, year=year, category="weather").first()
            pixels_exercises = Pixels.query.filter_by(
                user_id=user_id, year=year, category="exercises").first()
            pixels_reading = Pixels.query.filter_by(
                user_id=user_id, year=year, category="reading").first()
            pixels_health = Pixels.query.filter_by(
                user_id=user_id, year=year, category="health").first()
            ratings_array = {"rate": pixels_rate.ratings.split(","),
                             "anxiety": pixels_anxiety.ratings.split(","),
                             "mood": pixels_mood.ratings.split(","),
                             "weather": pixels_weather.ratings.split(","),
                             "exercises": pixels_exercises.ratings.split(","),
                             "reading": pixels_reading.ratings.split(","),
                             "health": pixels_health.ratings.split(",")}
            rate_weather_data = get_comparable_data(
                pixels_rate, pixels_weather)
            rate_exercises_data = get_comparable_data(
                pixels_rate, pixels_exercises)
            rate_reading_data = get_comparable_data(
                pixels_rate, pixels_reading)
            anxiety_weather_data = get_comparable_data(
                pixels_anxiety, pixels_weather)
            anxiety_exercises_data = get_comparable_data(
                pixels_anxiety, pixels_exercises)
            anxiety_reading_data = get_comparable_data(
                pixels_anxiety, pixels_reading)
            mood_weather_data = get_comparable_data(
                pixels_mood, pixels_weather)
            mood_exercises_data = get_comparable_data(
                pixels_mood, pixels_exercises)
            mood_reading_data = get_comparable_data(
                pixels_mood, pixels_reading)
            health_weather_data = get_comparable_data(
                pixels_health, pixels_weather)
            health_exercises_data = get_comparable_data(
                pixels_health, pixels_exercises)
            health_reading_data = get_comparable_data(
                pixels_health, pixels_reading)
            stats = []
            if correlation(5, 6, rate_weather_data):
                stats.append(
                    """You usually give higher rating to days in which\
there were sunny weather.""")
            elif correlation(5, 6, rate_weather_data, reverse=True):
                stats.append(
                     """You usually give higher rating to days in which\
 there were snowy/rainy weather.""")
            if correlation(5, 3, rate_exercises_data):
                stats.append(
                    """You usually give higher rating to days in which you\
exercise a lot.""")
            elif correlation(5, 3, rate_exercises_data, reverse=True):
                stats.append(
                    """You usually give higher rating to days in which you\
 don't exercise a lot.""")
            if correlation(5, 80, rate_reading_data):
                stats.append(
                    """You usually give higher rating to days in which you\
 read a lot.""")
            elif correlation(5, 80, rate_reading_data, reverse=True):
                stats.append(
                    """You usually give higher rating to days in which you\
 don't read a lot.""")
            if correlation(4, 6, anxiety_weather_data):
                stats.append("""Your anxiety was lower on days in which there\
 there were sunny weather.""")
            elif correlation(4, 6, anxiety_weather_data, reverse=True):
                stats.append("""Your anxiety was lower on days in which there\
 there were snowy/rainy weather.""")
            if correlation(4, 3, anxiety_exercises_data):
                stats.append("""Your anxiety was lower on days in which you\
 exercised a lot.""")
            elif correlation(4, 3, anxiety_exercises_data, reverse=True):
                stats.append("""Your anxiety was lower on days in which you\
 exercised a lot.""")
            if correlation(4, 80, anxiety_reading_data):
                stats.append("""Your anxiety was lower on days in which you\
 read a lot.""")
            elif correlation(4, 80, anxiety_reading_data, reverse=True):
                stats.append("""Your anxiety was lower on days in which you\
 didn't read a lot.""")
            if correlation(5, 6, mood_weather_data):
                stats.append("""You rate your mood better on sunny days\
""")
            elif correlation(5, 6, mood_weather_data, reverse=True):
                stats.append("""You rate your mood better on snowy/rainy days\
""")
            if correlation(5, 3, mood_exercises_data):
                stats.append("""You rate your mood better on days you exercise\
 a lot""")
            elif correlation(5, 3, mood_exercises_data, reverse=True):
                stats.append("""You rate your mood better on days you don't\
 exercise a lot""")
            if correlation(5, 80, mood_reading_data):
                stats.append("""You rate your mood better on days you read\
 a lot""")
            elif correlation(5, 80, mood_reading_data, reverse=True):
                stats.append("""You rate your mood better on days you don't\
 read a lot""")
            if correlation(4, 6, health_weather_data):
                stats.append("""You felt more healthy on days where there\
 were sunny weather""")
            elif correlation(4, 6, health_weather_data, reverse=True):
                stats.append("""You felt more healthy on days where there\
 were snowy/rainy weather""")
            if correlation(4, 3, health_exercises_data):
                stats.append("""You felt more healthy on days where you\
 exercised a lot""")
            elif correlation(4, 3, health_exercises_data, reverse=True):
                stats.append("""You felt more healthy on days where you\
 didn't exercised a lot""")
            if correlation(4, 80, health_reading_data):
                stats.append("""You felt more healthy on days where you\
 read a lot""")
            elif correlation(4, 80, health_reading_data, reverse=True):
                stats.append("""You felt more healthy on days where you\
 didn't read a lot""")
            week_days = (
                "Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday")
            pixels_zipped, best_day_index, best_day_date, worst_day_index,\
                worst_day_date = best_or_worst_day(
                    ratings_array, year, "best_and_worst")
            best_day = {
                    "date": "{}, {}".format(
                        week_days[best_day_date.weekday()],
                        datetime.strftime(best_day_date, "%Y-%m-%d")),
                    "pixels": {
                        "rate": pixels_zipped[best_day_index][0],
                        "anxiety": pixels_zipped[best_day_index][1],
                        "mood": pixels_zipped[best_day_index][2],
                        "weather": pixels_zipped[best_day_index][3],
                        "exercises": pixels_zipped[best_day_index][4],
                        "reading": pixels_zipped[best_day_index][5],
                        "health": pixels_zipped[best_day_index][6]
                    }}
            worst_day = {
                    "date": "{}, {}".format(
                        week_days[worst_day_date.weekday()],
                        datetime.strftime(worst_day_date, "%Y-%m-%d")),
                    "pixels": {
                        "rate": pixels_zipped[worst_day_index][0],
                        "anxiety": pixels_zipped[worst_day_index][1],
                        "mood": pixels_zipped[worst_day_index][2],
                        "weather": pixels_zipped[worst_day_index][3],
                        "exercises": pixels_zipped[worst_day_index][4],
                        "reading": pixels_zipped[worst_day_index][5],
                        "health": pixels_zipped[worst_day_index][6]
                    }}
            response_json = {
                "best_day": best_day,
                "worst_day": worst_day,
                "correlations": stats
            }
            response = Response(
                json.dumps(response_json),
                status=200, mimetype='application/json')
        return response
