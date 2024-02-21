from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, HiddenField
from wtforms.validators import Length, EqualTo, InputRequired


class ResetPasswordForm(FlaskForm):
    password1 = PasswordField(
        'Введите новый пароль',
        validators=(InputRequired('Это поле обязательно'), Length(min=6)),
    )
    password2 = PasswordField(
        'Подтвердите пароль',
        validators=(InputRequired('Это поле обязательно'), EqualTo('password1', 'Пароли не совпадают'))
    )
    admin_id = HiddenField()
    submit = SubmitField('Восстановить')
