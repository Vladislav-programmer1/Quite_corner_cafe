from flask_wtf import FlaskForm
from wtforms import StringField, TelField, PasswordField, SubmitField
from wtforms.validators import equal_to, DataRequired

from forms.registration import validate_text_values, validate_not_text_values


class ChangeUserDataForm(FlaskForm):
    name = StringField('Имя', validators=[validate_text_values, DataRequired()])
    surname = StringField('Фамилия', validators=[validate_text_values, DataRequired()])
    phone_number = TelField('Номер телефона (с кода страны)', validators=[validate_not_text_values, DataRequired()])
    password = PasswordField('Новый пароль')
    repeat_password = PasswordField('Повтор пароля',
                                    validators=[equal_to('password', message='Пароли не совпадают')])
    submit = SubmitField('Подтвердить')
