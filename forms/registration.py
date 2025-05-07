import asyncio

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, PasswordField, TelField, RadioField, Field
from wtforms.validators import DataRequired, Email, equal_to, ValidationError

from api import validate_email, validate_phone_number


def validate_text_values(form: FlaskForm, field: Field):
    if not str(field.data).isalpha():
        if form:
            pass
        raise ValidationError('В данном поле допустимы только буквы')


def email_validation(form: FlaskForm, field: Field):
    if form:
        pass
    if not asyncio.run(validate_email(field.data)):
        raise ValidationError("Некорректный email")


def phone_validation(form: FlaskForm, field: Field):
    if form:
        pass
    if not asyncio.run(validate_phone_number(field.data)):
        raise ValidationError("Некорректный номер телефона")


def validate_not_text_values(form: FlaskForm, field: Field):
    if form:
        pass
    if any(x.isalpha() for x in field.data):
        raise ValidationError("В этом поле недопустимы буквы")


class SignupForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), validate_text_values])
    surname = StringField("Фамилия", validators=[DataRequired(), validate_text_values])
    sex = RadioField("Пол", choices=['Мужской', 'Женский'], validators=[DataRequired()])
    email = EmailField('E-mail', validators=[Email(), DataRequired(), email_validation])
    phone_number = TelField('Номер телефона', validators=[DataRequired(), validate_not_text_values, phone_validation])
    password = PasswordField('Пароль', validators=[DataRequired(), ])
    repeated_password = PasswordField('Повтор пароля',
                                      validators=[DataRequired(), equal_to('password', message='Пароли не совпадают')])
    submit = SubmitField("Зарегистрироваться")
