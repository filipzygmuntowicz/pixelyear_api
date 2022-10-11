from exceptions import *
from setup import api
from functions import *
from api_endpoints.main import *
from api_endpoints.smaller_utility import *
from api_endpoints.user_account import *
from api_endpoints.statistics import *
from api_endpoints.journal import JournalEndpoint
#   use this code to run the app
#   adding all of the api waypoints

api.add_resource(Statistics, "/api/statistics/<string:year>")
api.add_resource(Main, "/api/<string:year>/<string:category>")
api.add_resource(Mean, "/api/mean/<string:year>")
api.add_resource(
    DaysWithActiveJournal, "/api/days_with_active_journal/<string:year>")
api.add_resource(MeanCategory, "/api/mean/<string:year>/<string:category>")
api.add_resource(YearsWithActivePixel,
                 "/api/active_years")
api.add_resource(UpdatedToday, "/api/updated_today")
api.add_resource(
    UpdatedTodayCategory, "/api/updated_today/<string:category>")
api.add_resource(Logging, "/api/login")
api.add_resource(Register, "/api/register")
api.add_resource(
    CreatePasswordResetToken, "/api/create_password_reset_token")
api.add_resource(
    ResetPassword, "/api/reset_password")
api.add_resource(ClearLoggedSessions, "/api/clear_logged_sessions")
api.add_resource(JournalEndpoint, "/api/journal/<string:date>")
api.add_resource(UploadAvatar, "/api/upload_avatar")
api.add_resource(DownloadAvatar, "/api/avatar/<string:uuid>")
api.add_resource(DeleteAccount, "/api/delete_account")
api.add_resource(FacebookLogin, "/api/facebook_login")
api.add_resource(GoogleLogin, "/api/google_login")

db.create_all()
if __name__ == '__main__':
    app.run(host='0.0.0.0')
