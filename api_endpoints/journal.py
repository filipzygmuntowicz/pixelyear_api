from functions import *


class Journal_endpoint(Resource):
    #   returns journal's entry for a given day
    def get(self, date):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            entry = Journal.query.filter_by(
                user_id=user_id, date=date).first()
            if entry is not None:
                response = Response(
                    json.dumps({"content": entry.content}),
                    status=200, mimetype='application/json')
            else:
                response = Response(
                    json.dumps({"error": "Entry not found!"}),
                    status=400, mimetype='application/json')
        return response

    #   inserts a new journal's entry into database
    def post(self, date):
        response, user_id, journal_content = \
            verify_jwt_and_check_for_empty("journal_content")
        if response.status == "200 OK":
            date = datetime.strptime(date, "%Y-%m-%d")
            if Journal.query.filter_by(
                    user_id=user_id, date=date).first() is None:
                new_entry = Journal(journal_content, user_id, date)
                db.session.add(new_entry)
                db.session.commit()
                response = Response(
                    json.dumps({"success": "Successfully added entry."}),
                    status=201, mimetype='application/json')
            else:
                response = Response(
                    json.dumps({"error": "Entry already exists!"}),
                    status=400, mimetype='application/json')
        return response

    #   changes an entry for a given date
    def patch(self, date):

        response, user_id, journal_content = \
            verify_jwt_and_check_for_empty("journal_content")
        if response.status == "200 OK":
            date = datetime.strptime(date, "%Y-%m-%d")
            entry_to_patch = Journal.query.filter_by(
                user_id=user_id, date=date).first()
            if entry_to_patch is not None:
                entry_to_patch.content = journal_content
                db.session.add(entry_to_patch)
                db.session.commit()
                response = Response(
                    json.dumps({"success": "Successfully changed entry."}),
                    status=200, mimetype='application/json')
            else:
                response = Response(
                    json.dumps({"error": "Entry not found!"}),
                    status=400, mimetype='application/json')
        return response
