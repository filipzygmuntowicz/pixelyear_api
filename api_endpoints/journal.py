from functions import *


class JournalEndpoint(Resource):
    #   returns journal's entry for a given day
    def get(self, date):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            entry = Journal.query.filter_by(
                user_id=user_id, date=date).first()
            entry_content = ""
            if entry is not None:
                entry_content = entry.content
            response = Response(
                json.dumps({"content": entry_content}),
                status=200, mimetype='application/json')
        return response

    #   changes an entry for a given date
    def patch(self, date):

        response, user_id, journal_content = \
            verify_jwt_and_check_for_empty("journal_content")
        if response.status == "200 OK":
            date = datetime.strptime(date, "%Y-%m-%d")
            entry_to_patch = Journal.query.filter_by(
                user_id=user_id, date=date).first()
            if entry_to_patch is None:
                entry_to_patch = Journal(journal_content, user_id, date)
            entry_to_patch.content = journal_content
            db.session.add(entry_to_patch)
            db.session.commit()
            response = Response(
                json.dumps({"success": "Successfully changed entry."}),
                status=200, mimetype='application/json')
        return response
