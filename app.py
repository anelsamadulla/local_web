import os
from flask import Flask
from dotenv import load_dotenv
from service.filters import load_custom_filters

from api.api import api_bp
from general.general import general_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

    app.register_blueprint(general_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    return app


if __name__ == '__main__':
    load_dotenv()
    app = create_app()
    load_custom_filters(app)
    app.run(debug=True, host='0.0.0.0')
