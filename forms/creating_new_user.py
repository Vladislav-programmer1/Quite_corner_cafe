from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange

from .registration import SignupForm


class CreatingNewUserForm(SignupForm):
    user_level = IntegerField('Уровень доступа', validators=[DataRequired(), NumberRange(1, 3)])
