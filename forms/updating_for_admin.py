from wtforms import RadioField, EmailField
from wtforms.validators import DataRequired

from .registration import Email, email_validation
from .update_user_data import ChangeUserDataForm


class ChangeUserDataForAdminsForm(ChangeUserDataForm):
    sex = RadioField('Пол', choices=['Женский', 'Мужской'], validators=[DataRequired(), ])
    email = EmailField("Email", validators=[DataRequired(), Email(), email_validation])

