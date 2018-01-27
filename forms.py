from flask_wtf import Form
import wtforms
from wtforms import validators


class LoginForm(Form):

    email = wtforms.StringField(
        validators=[validators.DataRequired(), validators.Email()],
        description='Email address')

    password = wtforms.PasswordField(
        validators=[validators.DataRequired()],
        description='Password')


class TestForm(Form):
    name = wtforms.StringField(
        validators=[validators.DataRequired()],
        description='Ключевые слова через запятую'
    )
