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
from forms import SeachForm

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
    form = SeachForm(request.form)
    return render_template('index.html', method=request.method, login_form=login_form, seach_form = form)

@app.route("/result/")
def result():
    seach_form = SeachForm(request.args)
    print(seach_form.region.data)
    print(seach_form.keywords.data)
    print(seach_form.date_to.data)
    print(seach_form.date_from.data)

    return render_template('result.html', method=request.method, seach_form = seach_form)


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

if __name__ == "__main__":
    app.run(debug=True)
