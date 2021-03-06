"""questions view"""
import datetime

from flask import jsonify, request, Blueprint
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.db.dbFunctions import post_new_question, is_question_exist, get_user_by_username, get_all_questions, \
    get_single_question, get_all_answers_to_question, delete_question, get_all_user_questions
from app.models import Question
from validation import FieldValidation

validate = FieldValidation()
question_blueprint = Blueprint("question_blueprint", __name__)


class PostQuestion(MethodView):
    """class to add questions"""
    @jwt_required
    def post(self):
        """method to add questions"""
        try:
            data = request.get_json()
            search_keys = ("title", "question")
            if all(key in data.keys() for key in search_keys):
                now = datetime.datetime.now()
                loggedin_user = get_jwt_identity()
                user = get_user_by_username(user_name=loggedin_user["username"], password=loggedin_user["password"])
                qstn_owner = user["username"]
                title = data.get("title").strip()
                question = data.get("question").strip()
                date = now.strftime("%Y-%m-%d %H:%M")
                validation = validate.validate_question(title, question)
                if validation:
                    return validation
                does_qstn_exist = is_question_exist(question)
                if does_qstn_exist:
                    return jsonify({"message": "Question already exists, check it out for an answer"}), 409
                post_new_question(title=title, question=question, qstn_owner=qstn_owner, date=date)
                new_question = Question(title=title, question=question, qstn_owner=qstn_owner, date=date)
                return jsonify({"message": "Question posted successfully", "New Question Posted": new_question.__dict__}), 201
            return jsonify({"message": "a 'key(s)' is missing in your question body"}), 400
        except:
            return jsonify({"message": "All fields are required"}), 400


class FetchAllQuestions(MethodView):
    """class to view all questions"""
    @jwt_required
    def get(self):
        """method to view all questions"""
        all_questions = get_all_questions()
        if all_questions:
            return jsonify({"message": "All questions viewed successfully", "questions": all_questions}), 200
        return jsonify({"message": "No questions posted yet"}), 404


class FetchSingleQuestion(MethodView):
    """class to view one questions"""
    @jwt_required
    def get(self, qstn_id):
        """method to view one questions"""
        try:
            id_validation = validate.validate_entered_id(qstn_id)
            if id_validation:
                return id_validation
            question_details = get_single_question(qstn_id=qstn_id)
            all_answers = get_all_answers_to_question(qstn_id=qstn_id)
            if question_details:
                return jsonify({"message": "success", "Question Details": question_details, "Answers": all_answers}), 200
            return jsonify({"message": "Question does not exist"}), 404
        except:
            return jsonify({"message": "Check your url and try again"}), 400


class DeleteQuestion(MethodView):
    """class to delete all questions"""
    @jwt_required
    def delete(self, qstn_id):
        """method to delete all questions"""
        try:
            id_validation = validate.validate_entered_id(qstn_id)
            if id_validation:
                return id_validation
            loggedin_user = get_jwt_identity()
            question_details = get_single_question(qstn_id=qstn_id)
            if question_details:
                delete_question(qstn_id, loggedin_user["username"])
                return jsonify({"message": "Question successfully deleted"}), 200
            return jsonify({"message": "Question does not exist"}), 404
        except:
            return jsonify({"message": "Check your url and try again"}), 400


class FetchAllUserQuestions(MethodView):
    """class to view all user questions"""
    @jwt_required
    def get(self):
        """method to view all user questions"""
        loggedin_user = get_jwt_identity()
        user = get_user_by_username(user_name=loggedin_user["username"], password=loggedin_user["password"])
        qstn_owner = user["username"]
        user_questions = get_all_user_questions(user_name=qstn_owner)
        if user_questions:
            return jsonify({"questions": user_questions}), 200
        return jsonify({"message": "user has no questions"}), 404


post_question_view = PostQuestion.as_view("post_question_view")
fetch_questions_view = FetchAllQuestions.as_view("fetch_questions_view")
fetch_one_question_view = FetchSingleQuestion.as_view("fetch_one_question_view")
delete_one_question_view = DeleteQuestion.as_view("delete_one_question_view")
get_user_questions_view = FetchAllUserQuestions.as_view("get_user_questions_view")

question_blueprint.add_url_rule("/api/v1/questions", view_func=post_question_view, methods=["POST"])
question_blueprint.add_url_rule("/api/v1/questions", view_func=fetch_questions_view, methods=["GET"])
question_blueprint.add_url_rule("/api/v1/questions/<qstn_id>", view_func=fetch_one_question_view, methods=["GET"])
question_blueprint.add_url_rule("/api/v1/questions/<qstn_id>", view_func=delete_one_question_view, methods=["DELETE"])
question_blueprint.add_url_rule("/api/v1/questions/user_questions", view_func=get_user_questions_view, methods=["GET"])
