import datetime

from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    all_history_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    correctly_history_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    all_geography_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    correctly_geography_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    all_science_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    correctly_science_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    all_literature_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    correctly_literature_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    all_sport_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    correctly_sport_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    all_films_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    correctly_films_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    all_music_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    correctly_music_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    all_nature_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    correctly_nature_questions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    trophies = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f'<USER> {self.id} {self.name} {self.about}'