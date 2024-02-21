from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import InputRequired


class AddTenantAdminForm(FlaskForm):
    first_name = StringField('Имя', validators=(InputRequired('Это поле обязательно'), ))
    last_name = StringField('Фамилия', validators=(InputRequired('Это поле обязательно'), ))
    email = EmailField('Электронная почта')
    phone = StringField('Номер телефона')
    submit = SubmitField('Обновить')
