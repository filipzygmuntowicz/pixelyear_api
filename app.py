from exceptions import *
from setup import api
from functions import *
from api_endpoints.main import *
from api_endpoints.smaller_utility import *
from api_endpoints.user_account import *
from api_endpoints.statistics import *
from api_endpoints.journal import Journal_endpoint
#   use this code to run the app
#   adding all of the api waypoints

api.add_resource(Statistics, "/api/statistics/<string:year>")
api.add_resource(Main, "/api/<string:year>/<string:category>")
api.add_resource(Mean, "/api/mean/<string:year>")
api.add_resource(
    Days_with_active_journal, "/api/days_with_active_journal/<string:year>")
api.add_resource(Mean_category, "/api/mean/<string:year>/<string:category>")
api.add_resource(Years_with_active_pixel,
                 "/api/active_years")
api.add_resource(Updated_today, "/api/updated_today")
api.add_resource(
    Updated_today_category, "/api/updated_today/<string:category>")
api.add_resource(Logging, "/api/login")
api.add_resource(Register, "/api/register")
api.add_resource(
    Create_password_reset_token, "/api/create_password_reset_token")
api.add_resource(
    Reset_password, "/api/reset_password")
api.add_resource(Clear_logged_sessions, "/api/clear_logged_sessions")
api.add_resource(Journal_endpoint, "/api/journal/<string:date>")
api.add_resource(Upload_Avatar, "/api/upload_avatar")
api.add_resource(Download_Avatar, "/api/avatar/<string:uuid>")
api.add_resource(Delete_account, "/api/delete_account")
api.add_resource(Facebook_login, "/api/facebook_login")
api.add_resource(Google_login, "/api/google_login")

if __name__ == '__main__':
    app.run()
