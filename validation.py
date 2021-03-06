"""validation"""
import re
from flask import jsonify


class FieldValidation:
    """Field validation"""

    def register_validation(self, user_name, email, password):
        """register validation"""
        if not user_name:
            return jsonify({"message": "username is missing"}), 400
        if not email:
            return jsonify({"message": "email is missing"}), 400
        if not password:
            return jsonify({"message": "password is missing"}), 400
        if len(password) < 5:
            return jsonify({"message": "password should be at least 5 characters long"}), 400

    def login_validation(self, user_name, password):
        """login validation"""
        if not user_name:
            return jsonify({"message": "username is missing"}), 400
        if not password:
            return jsonify({"message": "password is missing"}), 400
        if len(password) < 5:
            return jsonify({"message": "password should be at least 5 characters long"}), 400

    def validate_entered_id(self, id):
        """id validation"""
        try:
            _id = int(id)
        except ValueError:
            return jsonify({"message": "Id should be an interger"}), 400

    def validate_question(self, title, question):
        """question validation"""
        if not title:
            return jsonify({"message": "No question title was given"}), 400
        if not question:
            return jsonify({"message": "No question was given"}), 400
        if len(title) < 4:
            return jsonify({"message": "Title has to be at least 4 characters long"}), 400
        if len(question) < 10:
            return jsonify({"message": "Question has to be at least 10 characters long"}), 400

    def validate_email(self, email):
        """email validation"""
        if len(email) > 7:
            if re.match(r'(^[a-zA-Z0-9_.]+@[a-zA-Z0-9]+\.[a-z.]+$)', email) is not None:
                return True
            return False
        return False

    def validate_type(self, input):
        """type validation"""
        if re.match("^[1-9]", input) is not None:
            return True
        return False

    def validate_characters(self, input):
        """character validation"""
        if re.search('[a-zA-Z]', input) is not None:
            return True
        return False

    def validate_answer(self, answer):
        """answer validation"""
        if not answer:
            return jsonify({"message": "No answer was given"}), 400
        if len(answer) < 10:
            return jsonify({"message": "Answer has to be at least 10 characters long"}), 400

    def validate_comment(self, comment):
        """comment validation"""
        if not comment:
            return jsonify({"message": "No comment was given"}), 400
        if len(comment) < 3:
            return jsonify({"message": "Comment has to be at least 3 characters long"}), 400
