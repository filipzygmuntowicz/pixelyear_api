# PREQUISITES:

You need to install the required libraries via:
```
pip3 install -r requirements.txt
```
and then run the api via:
```
python3 app.py
```
Or just use docker via:
```
docker-compose up
```
After running the app for the first time you will be asked to provide your database credentials, facebook oauth app id, facebook oauth app secret and email address with password. You can skip (just type anything in them) all of the credentials, if you don't want to use the features associated with them (ouath logins and resetting user's password), except for your database credentials. After first run the credentials are saved in .txt files, check setup.py for file names.
# USAGE
Categories to choose from: ["rate", "anxiety", "mood", "weather", "exercises", "reading", "health"].
Available endpoints:
# /api/<string:year>/<string:category>
  - `GET` returns pixels data for a given year and category. The format is different for "exercises" category. Examples:
  - `/api/2022/health`:
```json
{
    "january": "1333432343213213214112124422442",
    "february": "1212141242312311241431121422",
    "march": "3122123243234433212412243331113",
    "april": "334332133243331333332244413343",
    "may": "4113344343443413231343333424342",
    "june": "311342231324431443134233244423",
    "july": "3424444224411431133123433112431",
    "august": "2414342424411342144442232000000",
    "september": "000000000000000000000000000000",
    "october": "0000000000000000000000000000000",
    "november": "000000000000000000000000000000",
    "december": "0000000000000000000000000000000"
}
```
  - `/api/2022/exercises`:
```json
{
    "january":["4","3","1","5","4","4","4","2","3","1","4","4","4","1","4","4","3","4","1","4","2","1","2","2","3","4","4","2","4","4","3"],
    "february":["2","2","4","3","5","2","2","2","4","4","3","2","5","5","4","3","1","5","5","5","5","5","1","2","3","2","2","3"],
    "march":["4","5","3","5","4","5","5","3","1","2","2","3","2","5","1","5","4","3","4","3","4","2","2","4","5","2","2","3","1","5","5"],
    "april":["5","3","1","3","1","1","3","4","1","2","4","4","5","1","5","2","4","4","4","5","2","2","2","4","1","2","5","4","3","3"],
    "may":["2","3","3","4","3","2","3","5","3","1","3","5","3","5","4","3","1","1","4","5","1","1","2","2","5","2","4","2","2","5","1"],
    "june":["3","2","3","2","1","4","1","4","5","3","3","4","5","1","2","1","2","5","4","1","4","2","2","4","5","3","4","1","3","2"],
    "july":["1","3","3","2","5","2","2","3","5","3","2","5","1","5","3","4","4","1","1","1","4","1","5","2","3","5","3","3","1","4","2"],
    "august":["5","1","5","3","1","5","5","3","1","4","1","1","4","3","3","3","2","1","2","1","2","3","3","1","0","0","0","0","0","0","0"],
    "september":["0","0","0","23","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],
    "october":["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],
    "november":["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],
    "december":["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"]
}
```
- `PATCH with JSON body consisting of: ["pixel_values", "date"]` changes the values of a pixel on a given date to given new values in "pixel_values". The years in url and in "date" from JSON body need to match. Date needs to be in ISO 8601 format ("YYYY-M-D"). 
#  /api/statistics/<string:year>
  - `GET` returns statistics for a given year. Example:
```json
  {
    "best_day": {
        "date": "Monday, 2022-04-11",
        "pixels": {
            "rate": "5",
            "anxiety": "1",
            "mood": "5",
            "weather": "2",
            "exercises": "5",
            "reading": "7",
            "health": "4"
        }
    },
    "worst_day": {
        "date": "Wednesday, 2022-03-30",
        "pixels": {
            "rate": "1",
            "anxiety": "4",
            "mood": "1",
            "weather": "2",
            "exercises": "1",
            "reading": "6",
            "health": "1"
        }
    },
    "correlations": [
        "Your anxiety was lower on days in which you exercised a lot.",
        "Your anxiety was lower on days in which you didn't read a lot."
    ]
}
```
  
  # /api/mean/<string:year>/<string:category>?type={numeric}
   - `GET` returns mean for a given year and category, mode for "exercises" and "health" categories, arithmethic for all the others. You can skip category in url to get means of all categories. Also there is an optional argument ?type whether categories name should be replaced by their ids. Examples:
   - `/api/mean/2022/mood`
   
```json
{
  "mean": 3.05
}
```
  - `/api/mean/2022/all` or `/api/mean/2022`
```json
{
    "means": {
        "rate": 3.19,
        "anxiety": 2.48,
        "mood": 3.05,
        "weather": 3,
        "exercises": 3,
        "reading": 6,
        "health": 2.64
    }
}
```
    
# /api/active_years
  - `GET` returns a sorted list of years where the user has placed a pixel. Example:
```json
{
    "years": [
        2022
    ]
}
```
  # /api/updated_today/<string:category>?type={numeric}
   - `GET` returns information whether pixels in given category were edited today. /category in url is optional, if you skip it it will return information about all categories. Also there is an optional argument ?type whether categories name should be replaced by their ids. Examples:
   - `api/updated_today/reading`
```json
{
    "updated": {
        "health": "4"
    },
    "not_updated": []
}
```
  - `api/updated_today/all` or `api/updated_today`
```json
{
    "updated": {
        "rate": "3",
        "health": "4"
    },
    "not_updated": [
        "anxiety",
        "mood",
        "weather",
        "exercises",
        "reading"
    ]
}
```
  # /api/register
   - `POST with JSON body consisting of keys: ["email", "password", "repassword"]` registers the user. Returns error if passwords do not match or the email is taken.
  # /api/login
   - `POST with JSON body consisting of keys: ["email", "password", "never_expire"(optional) ]` returns JWT authorization token which needs to be put into Authorization header as Bearer Token. The token has an expiration date of 12 hour, it can be extended indifinitely with "never_expire" in JSON body set to True. Also returns user's uuid and email. Example:
```json
   {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiZTE0NGUxZDQtNDQzNy00ODRjLTkzNzctMDBlYjIwOGExYWIxIiwiY3JlYXRpb25fZGF0ZSI6IjIwMjItMDktMDMgMTQ6NTU6NDQuMzI0NTg0IiwiZXhwaXJhdGlvbl9kYXRlIjoiMjA1MC0wMS0xOCAxNDo1NTo0NC4zMjQ1ODQifQ.fB7a7xqufqdBOE5xtsXE7Wka37TD0oOl0_Xb3-HhUZI",
    "uuid": "e144e1d4-4437-484c-9377-00eb208a1ab1",
    "email": "test@test.pl"
}
```
  # /api/create_password_reset_token
   - `POST` creates a JWT token for a password reset and sends it to user via email.
  # /api/reset_password/<string:password_reset_token>
   - `POST with JSON body consisting of keys: ["password", "repassword"]` resets user's password if given token is correct and passwords from JSON body match.
  # /api/clear_logged_sessions
   - `PATCH` makes all login tokens for a given user obsolete.  

# /api/journal/<string:date>(ISO 8601)
  - `GET` - returns journal's content for given date. Example:
   - `api/journal/2022-09-11`
```json
  {
    "content": "Today I woke up."
}
```
  - `POST with JSON body consisting of keys: ["journal_content"]` - creates entry with content given in JSON's body.
  - `PATCH with JSON body consisting of keys: ["journal_content"]` - changes journal's content to the given in JSON's body.

# /api/days_with_active_journal/<string:year>
  - `GET` - returns data of a given year containing information of days where the user has updated the journal. Example:
    - `api/days_with_active_journal/2022`
```json
    {
      "journal_days": "0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1"
}
```
# /api/upload_avatar
  - `PATCH with form-data body consisting of keys: ["avatar"]` - uploads user's avatar, naming it by user's uuid, the avatar has to be in png, jpg or jpeg format.
# /api/avatar/<string:uuid>
  - `GET` - returns avatar of user with uuid given in url. If uuid is invalid or the user hasn't uploaded any avatar it returns the default avatar.
# /api/google_login
  - `POST  with JSON body consisting of keys: ["token", "state"]` - takes the google oauth access code, registers (if necessary) the user and returns the same JSON as in /api/login. Also verifies if state is valid.
# /api/facebook_login
  - `POST  with JSON body consisting of keys: ["code", "state"]` - takes the facebook oauth code, registers (if necessary) the user and returns the same JSON as in /api/login. Also verifies if state is valid. 
 
 ###### Filip Zygmuntowicz 2022
