import os
from flask import Flask
from dotenv import load_dotenv
from service.filters import load_custom_filters

from database import init_db
from general.general import general_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    init_db(app)
    app.register_blueprint(general_bp)
    return app


if __name__ == '__main__':
    load_dotenv()
    app = create_app()
    load_custom_filters(app)
    app.run(debug=True, host='0.0.0.0', port=5050)
