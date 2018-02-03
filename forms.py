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

class SeachForm(Form):

    keywords = wtforms.StringField(
        validators=[validators.DataRequired()],
        description='keywords')
    region = wtforms.SelectField(
        validators=[validators.DataRequired()],
        choices=[(1, 'Москва'), (2,'Санкт-Петербург')],
        description='city-select')
    date_from = wtforms.StringField(
        validators=[validators.DataRequired()],
        description='date_from')
    date_to = wtforms.StringField(
        validators=[validators.DataRequired()],
        description='date_to')