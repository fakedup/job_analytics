import hashlib
import uuid

import flask
from flask import Flask, request, redirect, url_for
from flask import render_template
from flask_login import UserMixin, login_user, LoginManager, logout_user
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

from forms import LoginForm
from forms import SearchForm

from app.analysis import *

app = flask.Flask(__name__)
app.config.from_object('config')  # !!!!!!!!!!!!!!!!!!!!!!!!!!!#

engine = sa.create_engine(app.config['DATABASE_CONNECTION_STRING'])
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

login_manager = LoginManager()
login_manager.init_app(app)
# Это нужно для того, чтобы модуль login_manager знал куда редиректить
# пользователя
login_manager.login_view = 'login'


# Требуется для работы модуля flask_login
@login_manager.user_loader
def load_user(email):
    return db_session.query(User).filter(User.email == email).first()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True)
    _password = sa.Column(sa.String, name='password')

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(
            (plaintext + salt).encode()).hexdigest()
        self._password = salt + '|' + hashed_password

    def check_password(self, plaintext):
        salt, hashed_password = self.password.split('|')
        return hashed_password == hashlib.sha512((plaintext + salt).encode()).hexdigest()

    def get_id(self):
        return self.email


@app.route("/", methods=['GET', 'POST'])
def index():
    login_form = LoginForm()
    search_form = SearchForm()
    return render_template(
        'index.html', method=request.method, search_form=search_form,
        login_form=login_form,
    )


@app.route("/result/", methods=['GET', 'POST'])
def result():
    login_form = LoginForm()
    search_form = SearchForm(request.args)
    if request.args.get('keywords') is not None:
        print(search_form.keywords.data)
        print(search_form.region.data)
        print(search_form.date_from.data)
        print(search_form.date_to.data)

    date_from = request.args.get('date_from') or '2016-09-01'
    date_to = request.args.get('date_to') or '2017-08-31'

    try:
        keywords = request.args.get('keywords').split(',')
    except AttributeError:
        keywords = ['Python']

    try:
        regions = [int(x) for x in request.args.get('regions').split(',')]
    except AttributeError:
        regions = [1]

    search_fields = request.args.get('search_fields') or 'title'

    vacancies = get_vacancies_df(
        get_vacancies_query(
            date_from, date_to, keywords, regions, search_fields
        ), dbs
    )

    nv_plot = get_number_vacancies_plot (vacancies, keywords)

    salary_bp = get_salaries_boxplot (vacancies)

    table = get_titles_pivot (vacancies).to_html()

    return render_template(
        'result.html',
        method=request.method,
        login_form=login_form,
        search_form=search_form,
        nv_plot=nv_plot,
        salary_bp=salary_bp,
        table=table,
    )


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_session.query(User).filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))

        flask.flash('Email or password is wrong.')

    return render_template('login.html', form=form)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(flask.url_for('index'))

@app.route("/test/", methods=['GET', 'POST'])
def test():
    # from forms import TestForm

    date_from = request.args.get('date_from') or '2016-09-01'
    date_to = request.args.get('date_to') or '2017-08-31'

    try:
        keywords = request.args.get('keywords').split(',')
    except AttributeError:
        keywords = ['Python']

    try:
        regions = [int(x) for x in request.args.get('regions').split(',')]
    except AttributeError:
        regions = [1]

    search_fields = request.args.get('search_fields') or 'title'

    vacancies = get_vacancies_df (
    get_vacancies_query (date_from, date_to, keywords, regions, search_fields),
    dbs)

    nv_plot = get_number_vacancies_plot (vacancies, keywords)

    salary_bp = get_salaries_boxplot (vacancies)

    table = get_titles_pivot (vacancies).to_html()

    form = TestForm(flask.request.args)

    # if form.validate():
    #     pass # Генерируем график

    return render_template('test.html', nv_plot=nv_plot, salary_bp = salary_bp, table = table)
    # return nv_plot


if __name__ == "__main__":
    app.run(debug=True)