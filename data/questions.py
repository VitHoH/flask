import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'question'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    first_answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    second_answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    third_answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    fourth_answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    correct_answer = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    col_answers = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    col_correct_answers = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    author = orm.relationship('User')

    def __repr__(self):
        return f'{self.question}'