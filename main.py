from random import randrange

from flask import Flask, render_template, redirect, jsonify
from flask import make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
import sys
from data import db_session
from data.questions import Question
from data.users import User
from forms.question import AddQuestionForm, QuestionForm
from forms.users import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html", title='Главная', dynamic_link=f'/profile/{current_user.id}')


@app.route('/question', methods=['GET', 'POST'])
@login_required
def add_question():
    form = AddQuestionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        question = Question()
        question.question = form.question.data
        question.first_answer = form.first_answer.data
        question.second_answer = form.second_answer.data
        question.third_answer = form.third_answer.data
        question.fourth_answer = form.fourth_answer.data
        question.correct_answer = form.true_answer.data
        question.category = form.category.data
        question.user_id = db_sess.query(User).filter(User.name == current_user.name).first().id
        db_sess.add(question)
        db_sess.commit()
        return redirect('/')
    return render_template('add_question.html', title='Добавление вопроса',
                           form=form, dynamic_link=f'/profile/{current_user.id}')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/question_start')
def start_question():
    db_sess = db_session.create_session()
    question = db_sess.query(Question).all()
    col = len(question)
    n_lvl = randrange(1, col)
    return redirect(f'question/{n_lvl}')


@app.route('/question/<int:id>', methods=['GET', 'POST'])
def question(id):
    form = QuestionForm()
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == id).first()
    if form.validate_on_submit():
        true_answer = question.correct_answer
        if true_answer == form.your_answer.data:
            question.col_correct_answers += 1
            question.col_answers += 1
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.trophies += 5
            if question.category == 'history':
                user.all_history_questions += 1
                user.correctly_history_questions += 1
            elif question.category == 'geography':
                user.all_geography_questions += 1
                user.correctly_geography_questions += 1
            elif question.category == 'music':
                user.all_music_questions += 1
                user.correctly_music_questions += 1
            elif question.category == 'science':
                user.all_science_questions += 1
                user.correctly_science_questions += 1
            elif question.category == 'literature':
                user.all_literature_questions += 1
                user.correctly_literature_questions += 1
            elif question.category == 'sport':
                user.all_sport_questions += 1
                user.correctly_sport_questions += 1
            elif question.category == 'film':
                user.all_film_questions += 1
                user.correctly_film_questions += 1
            elif question.category == 'nature':
                user.all_nature_questions += 1
                user.correctly_nature_questions += 1
        else:
            question.col_answers += 1
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.trophies -= 3
            if question.category == 'history':
                user.all_history_questions += 1
            elif question.category == 'geography':
                user.all_geography_questions += 1
            elif question.category == 'music':
                user.all_music_questions += 1
            elif question.category == 'science':
                user.all_science_questions += 1
            elif question.category == 'literature':
                user.all_literature_questions += 1
            elif question.category == 'sport':
                user.all_sport_questions += 1
            elif question.category == 'film':
                user.all_film_questions += 1
            elif question.category == 'nature':
                user.all_nature_questions += 1
        db_sess.commit()
        return redirect(f"/result/{question.id}/{form.your_answer.data}")
    try:
        proz_true_ans = question.col_answers / question.col_correct_answers * 100
    except ZeroDivisionError:
        proz_true_ans = 'На этот вопрос никто не отвечал'
    return render_template('question.html', question=question.question, first_answer=question.first_answer,
                           second_answer=question.second_answer, third_answer=question.third_answer,
                           fourth_answer=question.fourth_answer,
                           proz_true_ans=proz_true_ans,
                           col_answers=question.col_answers, form=form, dynamic_link=f'/profile/{current_user.id}',
                           author_href=f'/profile/{question.author_id}', author=question.author.name)


@app.route('/result/<int:id_question>/<int:your_answer>')
def result(id_question, your_answer):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == id_question).first()
    try:
        proz_true_ans = question.col_answers / question.col_correct_answers
    except ZeroDivisionError:
        proz_true_ans = 'На этот вопрос никто не отвечал'
    return render_template('result.html', question=question.question, first_answer=question.first_answer,
                           second_answer=question.second_answer, third_answer=question.third_answer,
                           fourth_answer=question.fourth_answer,
                           proz_true_ans=proz_true_ans,
                           col_answers=question.col_answers, your_answer=your_answer,
                           true_answer=question.correct_answer, dynamic_link=f'/profile/{current_user.id}',
                           author_href=f'/profile/{question.author_id}', author=question.author.name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile/<int:id>')
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()

    return render_template('profile.html', name=user.name, about=user.about, created_date=user.created_date)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/quiz.db")
    # questions = sys.stdin.read().split('\n')
    # for question in questions:
    #     question_this = question.split(',')
    #     print(question_this)
    #     db_sess = db_session.create_session()
    #     question = Question()
    #     question.question = question_this[0].strip()
    #     question.first_answer = question_this[1].strip()
    #     question.second_answer = question_this[2].strip()
    #     question.third_answer = question_this[3].strip()
    #     question.fourth_answer = question_this[4].strip()
    #     question.correct_answer = question_this[5].strip()
    #     question.category = 'history'
    #     question.author_id = 1
    #     db_sess.add(question)
    #     db_sess.commit()
    app.run()


if __name__ == '__main__':
    main()
