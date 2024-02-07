from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class TenantForm(FlaskForm):
    region = StringField('Регион')
    country = StringField('Страна')
    state = StringField('Область/Штат/Земля')
    city = StringField('Город')
    address = StringField('Адрес')
    address2 = StringField('Адрес 2')
    zip_code = StringField('Почтовый индекс')
    phone = StringField('Номер телефона')
    email = EmailField('Электронная почта', render_kw={'disabled':''})
    submit = SubmitField('Обновить')
    tenant_id = HiddenField('tenant_id')
    title = HiddenField('title')
