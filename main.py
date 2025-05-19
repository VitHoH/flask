from random import randrange

from flask import Flask, render_template, redirect, jsonify
from flask import make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from sqlalchemy import desc

from data import db_session
from data import question_api
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
    if current_user.is_authenticated:
        return render_template("index.html", title='Главная', dynamic_link=f'/profile/{current_user.id}')
    return render_template("index.html", title='Главная')


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
    if current_user.is_authenticated:
        return render_template('add_question.html', title='Добавление вопроса',
                               form=form, dynamic_link=f'/profile/{current_user.id}')
    return render_template('add_question.html', title='Добавление вопроса',
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


@app.route('/question_start')
def start_question():
    db_sess = db_session.create_session()
    question = db_sess.query(Question).all()
    col = len(question)
    n_lvl = randrange(1, col)
    return redirect(f'question/{n_lvl}')


@app.route('/question/<int:id>', methods=['GET', 'POST'])
@login_required
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
    if current_user.is_authenticated:
        return render_template('question.html', question=question.question, first_answer=question.first_answer,
                               second_answer=question.second_answer, third_answer=question.third_answer,
                               fourth_answer=question.fourth_answer,
                               proz_true_ans=proz_true_ans,
                               col_answers=question.col_answers, form=form, dynamic_link=f'/profile/{current_user.id}',
                               author_href=f'/profile/{question.author_id}', author=question.author.name,
                               title='Ответьте на вопрос')
    return render_template('question.html', question=question.question, first_answer=question.first_answer,
                           second_answer=question.second_answer, third_answer=question.third_answer,
                           fourth_answer=question.fourth_answer,
                           proz_true_ans=proz_true_ans,
                           col_answers=question.col_answers, form=form,
                           author_href=f'/profile/{question.author_id}', author=question.author.name,
                           title='Ответьте на вопрос')


@app.route('/result/<int:id_question>/<int:your_answer>')
@login_required
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
                           author_href=f'/profile/{question.author_id}', author=question.author.name,
                           title='Результаты ответа на вопрос')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile/<int:id>')
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    questions = db_sess.query(Question).filter(Question.author_id == id).all()
    col_question_created = len(questions)
    try:
        h_proz_cor_ans = f'{round(user.correctly_history_questions / user.all_history_questions, 1) * 100}%'
        print(user.correctly_history_questions)
    except ZeroDivisionError:
        h_proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы этой рубрики'
    try:
        g_proz_cor_ans = f'{round(user.correctly_geography_questions / user.all_geography_questions, 1) * 100}%'
    except ZeroDivisionError:
        g_proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы этой рубрики'
    try:
        s_proz_cor_ans = f'{round(user.correctly_science_questions / user.all_science_questions, 1) * 100}%'
    except ZeroDivisionError:
        s_proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы этой рубрики'
    try:
        l_proz_cor_ans = f'{round(user.correctly_literature_questions / user.all_literature_questions, 1) * 100}%'
    except ZeroDivisionError:
        l_proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы этой рубрики'
    try:
        sp_proz_cor_ans = f'{round(user.correctly_sport_questions / user.all_sport_questions, 1) * 100}%'
    except ZeroDivisionError:
        sp_proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы этой рубрики'
    try:
        f_proz_cor_ans = f'{round(user.correctly_films_questions / user.all_films_questions, 1) * 100}%'
    except ZeroDivisionError:
        f_proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы этой рубрики'
    try:
        m_proz_cor_ans = f'{round(user.correctly_music_questions / user.all_music_questions, 1) * 100}%'
    except ZeroDivisionError:
        m_proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы этой рубрики'
    try:
        n_proz_cor_ans = f'{round(user.correctly_nature_questions / user.all_nature_questions, 1) * 100}%'
    except ZeroDivisionError:
        n_proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы этой рубрики'
    questions_answered = user.all_history_questions + user.all_geography_questions + user.all_science_questions + user.all_literature_questions + user.all_sport_questions + user.all_films_questions + user.all_music_questions + user.all_nature_questions
    col_cor_ans = user.correctly_history_questions + user.correctly_films_questions + user.correctly_music_questions + user.correctly_sport_questions + user.correctly_nature_questions + user.correctly_literature_questions + user.correctly_geography_questions + user.correctly_science_questions
    try:
        proz_cor_ans = f'{round(col_cor_ans / questions_answered, 1) * 100}%'
    except ZeroDivisionError:
        proz_cor_ans = 'Пользователь ни разу не отвечал на вопросы'
    return render_template('profile.html', name=user.name, about=user.about, created_date=user.created_date.date(),
                           trophies=user.trophies, h_questions_answered=user.all_history_questions,
                           g_questions_answered=user.all_geography_questions,
                           s_questions_answered=user.all_science_questions,
                           l_questions_answered=user.all_literature_questions,
                           sp_questions_answered=user.all_sport_questions,
                           f_questions_answered=user.all_films_questions, m_questions_answered=user.all_music_questions,
                           n_questions_answered=user.all_nature_questions, col_question_created=col_question_created,
                           questions_answered=questions_answered, h_proz_cor_ans=h_proz_cor_ans,
                           g_proz_cor_ans=g_proz_cor_ans, s_proz_cor_ans=s_proz_cor_ans, l_proz_cor_ans=l_proz_cor_ans,
                           sp_proz_cor_ans=sp_proz_cor_ans, m_proz_cor_ans=m_proz_cor_ans,
                           f_proz_cor_ans=f_proz_cor_ans, n_proz_cor_ans=n_proz_cor_ans, proz_cor_ans=proz_cor_ans,
                           title=f"Профиль пользователя {user.name}")


@app.route('/leaderboard')
def leaderboard():
    db_sess = db_session.create_session()
    users = db_sess.query(User).order_by(desc(User.trophies), User.name).limit(20).all()
    return render_template('leaderboard.html', leaderboard=users, col_leaders=len(users), title="Таблица лидеров")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/quiz.db")
    # для списка объектов
    api.add_resource(question_api.QuestionListResource, '/api/question')

    # для одного объекта
    api.add_resource(question_api.QuestionResource, '/api/question/<int:question_id>')
    app.run()


if __name__ == '__main__':
    main()
