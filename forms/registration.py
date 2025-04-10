from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, equal_to


class SignupForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired(), ])
    email = EmailField('E-mail', validators=[Email(), DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), ])
    repeated_password = PasswordField('Повтор пароля',
                                      validators=[DataRequired(), equal_to(password, message='Пароли не совпадают')])
    submit = SubmitField("Зарегистрироваться")
