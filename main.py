import datetime

from flask import Flask, render_template, redirect, request, abort, jsonify
from data import db_session
from data.users import User
from forms.question import QuestionForm
from forms.users import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import make_response
from flask_restful import reqparse, abort, Api, Resource
from data.questions import Question


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
    return render_template("index.html", title='Главная')


@app.route('/question',  methods=['GET', 'POST'])
@login_required
def add_question():
    form = QuestionForm()
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
        db_sess = db_session.create_session()
        print(current_user)
        question.user_id = db_sess.query(User).filter(User.name == current_user.name).first().id
        db_sess.add(question)
        db_sess.commit()
        return redirect('/')
    return render_template('question.html', title='Добавление вопроса',
                           form=form)


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/quiz.db")
    q = Question()
    print(q)
    app.run()


if __name__ == '__main__':
    main()