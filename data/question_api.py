from flask import jsonify
from flask_restful import reqparse, abort, Resource
from . import db_session
from .questions import Question


def abort_if_question_not_found(question_id):
    session = db_session.create_session()
    question = session.query(Question).get(question_id)
    if not question:
        abort(404, message=f"Question {question_id} not found")


class QuestionResource(Resource):
    def get(self, question_id):
        abort_if_question_not_found(question_id)
        session = db_session.create_session()
        question = session.query(Question).get(question_id)
        return jsonify({'question': question.to_dict(
            only=('question', 'first_answer', 'second_answer', 'third_answer', 'fourth_answer', 'correct_answer',
                  'category'))})

    def delete(self, question_id):
        abort_if_question_not_found(question_id)
        session = db_session.create_session()
        question = session.query(Question).get(question_id)
        session.delete(question)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('question', required=True)
parser.add_argument('first_answer', required=True)
parser.add_argument('second_answer', required=True)
parser.add_argument('third_answer', required=True)
parser.add_argument('fourth_answer', required=True)
parser.add_argument('correct_answer', required=True, type=int)
parser.add_argument('category', required=True)
parser.add_argument('author_id', required=True, type=int)


class QuestionListResource(Resource):
    def get(self):
        session = db_session.create_session()
        question = session.query(Question).all()
        return jsonify({'question': [item.to_dict(
            only=(
            'question', 'first_answer', 'second_answer', 'third_answer', 'fourth_answer', 'correct_answer', 'category',
            'author_id')) for item in question]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        question = Question(
            question=args['question'],
            first_answer=args['first_answer'],
            second_answer=args['second_answer'],
            third_answer=args['third_answer'],
            fourth_answer=args['fourth_answer'],
            correct_answer=args['correct_answer'],
            category=args['category'],
            author_id=args['author_id'],
        )
        session.add(question)
        session.commit()
        return jsonify({'id': question.id})
