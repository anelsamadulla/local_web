from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
ma = Marshmallow()


def init_db(app):
    db.init_app(app)
    ma.init_app(app)
    # with app.app_context():
    #     db.create_all()
