from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired


class TenantAdminForm(FlaskForm):
    first_name = StringField('Имя', validators=(DataRequired('Это поле обязательно'), ))
    last_name = StringField('Фамилия', validators=(DataRequired('Это поле обязательно'), ))
    phone = StringField('Номер телефона')
    email = EmailField('Электронная почта')
    admin_id = HiddenField()
    admin_password = PasswordField('Новый пароль')
    submit = SubmitField('Обновить')
