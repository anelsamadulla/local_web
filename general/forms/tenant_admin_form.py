from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired


class TenantAdminForm(FlaskForm):
    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    phone = StringField('Номер телефона')
    email = StringField('Электронная почта')
    admin_id = HiddenField()
    admin_password = PasswordField('Новый пароль') 
    submit = SubmitField('Обновить')
