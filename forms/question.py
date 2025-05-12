from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    question = StringField('Вопрос', validators=[DataRequired()])
    first_answer = TextAreaField("Первый ответ")
    second_answer = TextAreaField("Второй ответ")
    third_answer = TextAreaField("Третий ответ")
    fourth_answer = TextAreaField("Четвёртый ответ")
    true_answer = IntegerField('Номер правильного ответа')
    category = RadioField('Категория',
                          choices=[("history", "История"), ("geography", "География"), ("science", "Наука"),
                                   ("literature", "Литература"), ("sport", "Спорт"), ("film", "Фильмы"),
                                   ("music", "Музыка"), ("nature", "Природа")])
    submit = SubmitField('Применить')
