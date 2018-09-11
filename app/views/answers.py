import datetime

from flask import jsonify, request, Blueprint
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.db.dbFunctions import get_user_by_username, get_single_question, get_question_by_id, is_answer_exist, \
    post_new_answer, update_answer, get_answer_details, accept_answer, get_answer_by_id
from app.models import Answer
from app.validation import FieldValidation

validate = FieldValidation()
answer_blueprint = Blueprint("answer_blueprint", __name__)


class PostAnswerToQuestion(MethodView):
    """class to post an answer to a question"""

    @jwt_required
    def post(self, qstn_id):
        try:
            data = request.get_json()

            if "answer" in data.keys():
                answer = data.get("answer").strip()

                now = datetime.datetime.now()
                date = now.strftime("%Y-%m-%d %H:%M")
                vote = 0
                status = "pending"

                loggedin_user = get_jwt_identity()
                user = get_user_by_username(user_name=loggedin_user["username"], password=loggedin_user["password"])
                ans_owner = user["username"]

                id_validation = validate.validate_entered_id(qstn_id)
                if id_validation:
                    return id_validation

                ans_validation2 = validate.validate_answer(answer)
                if ans_validation2:
                    return ans_validation2

                ans_validation = validate.validate_characters(answer)
                if not ans_validation:
                    return jsonify({"message": "wrong answer format entered, Please try again"}), 400

                does_answer_exist = is_answer_exist(qstn_id=qstn_id, answer=answer)
                if does_answer_exist:
                    return jsonify({"message": "Such an answer is already given for this same question, please try "
                                               "with another one "
                                    }), 409

                does_qstn_exist = get_question_by_id(qstn_id=qstn_id)
                if not does_qstn_exist:
                    return jsonify({"message": " No such question exists"}), 404

                post_new_answer(
                    answer=answer,
                    ans_owner=ans_owner,
                    qstn_id=qstn_id,
                    vote=vote,
                    status=status,
                    date=date)
                new_answer = Answer(
                    answer=answer,
                    ans_owner=ans_owner,
                    qstn_id=qstn_id,
                    vote=vote,
                    status=status,
                    date=date)
                return jsonify({'New Answer Posted': new_answer.__dict__}), 201
            return jsonify({"message": "a 'key' is missing in your answer body"}), 400
        except Exception as exception:
            return jsonify({"message": exception}), 400


class UpDateAnswer(MethodView):
    """class to update an answer"""

    @jwt_required
    def put(self, qstn_id, ans_id):
        try:
            qstn_id_validation = validate.validate_entered_id(qstn_id)
            if qstn_id_validation:
                return qstn_id_validation

            ans_id_validation = validate.validate_entered_id(ans_id)
            if ans_id_validation:
                return ans_id_validation

            loggedin_user = get_jwt_identity()
            user = get_user_by_username(user_name=loggedin_user["username"], password=loggedin_user["password"])
            current_user = user["username"]

            does_answer_exist = get_answer_by_id(ans_id=ans_id, qstn_id=qstn_id)
            does_qstn_exist = get_question_by_id(qstn_id=qstn_id)
            ans_owner = get_answer_details(qstn_id, ans_id)
            question_details = get_single_question(qstn_id=qstn_id)

            if does_qstn_exist:
                if does_answer_exist:
                    if current_user == ans_owner["ans_owner"]:
                        data = request.get_json()

                        if "answer" in data.keys():
                            answer = data.get("answer").strip()

                            ans_validation2 = validate.validate_answer(answer)
                            if ans_validation2:
                                return ans_validation2

                            ans_validation = validate.validate_characters(answer)
                            if not ans_validation:
                                return jsonify({"message": "wrong answer format entered, Please try again"}), 400

                            update = update_answer(answer=answer, ans_id=ans_id, qstn_id=qstn_id)
                            updated_answer = get_answer_details(qstn_id=qstn_id, ans_id=ans_id)
                            return jsonify({"message": update, "Updated answer": updated_answer}), 200

                        return jsonify({"message": "Answer 'key' is missing"}), 400
                    if current_user == question_details["qstn_owner"]:
                        status = "Accepted"

                        accept = accept_answer(status=status, qstn_id=qstn_id, ans_id=ans_id)
                        updated_answer = get_answer_details(qstn_id=qstn_id, ans_id=ans_id)
                        return jsonify({"message": accept, "Updated answer": updated_answer}), 200
                    return jsonify({"message": "No such answer exists"}), 404
                return jsonify({"message": "No such question exists any more"}), 404
        except Exception as exception:
            return jsonify({"message": exception}), 400


post_answer_view = PostAnswerToQuestion.as_view("post_answer_view")
update_answer_view = UpDateAnswer.as_view("update_answer_view")

answer_blueprint.add_url_rule("/api/v1/questions/<qstn_id>/answers", view_func=post_answer_view, methods=["POST"])
answer_blueprint.add_url_rule("/api/v1/questions/<qstn_id>/answers/<ans_id>", view_func=update_answer_view,
                              methods=["PUT"])