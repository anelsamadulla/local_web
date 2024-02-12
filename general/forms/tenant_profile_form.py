from flask_wtf import FlaskForm
from wtforms import StringField, EmailField


class TenantForm(FlaskForm):
    max_devices = StringField('Макс. устройств', render_kw={'disabled':''})
    max_assets = StringField('Макс. активов', render_kw={'disabled':''})
    max_customers = StringField('Макс. клиентов', render_kw={'disabled':''})
    max_users = StringField('Макс. пользователей', render_kw={'disabled':''})
    