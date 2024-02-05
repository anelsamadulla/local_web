from app import app


def get_basedir():
    return app.config.BASEDIR
