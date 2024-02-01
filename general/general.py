import os
import json
from datetime import date

import jwt
from flask import Blueprint, redirect, render_template, request, url_for
from config import basedir
from service.tb import init


general_bp = Blueprint(
    'general_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/assets'
)


@general_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files['generated_key']
        f.save(os.path.join(basedir, 'generated_key.json'))
        return redirect(url_for('general_bp.index'))

    if request.method == 'GET':
        data = {}

        filepath = os.path.join(basedir, 'generated_key.json')
        if not os.path.exists(filepath):
            return redirect(url_for('general_bp.loadkey'))

        data = json.load(open(filepath))
        data['protected_data'] = jwt.decode(data['jwt_token'], options={"verify_signature": False})
        data['license_status'] = date.today() < date.fromtimestamp(data['protected_data']['expires_at'])
        data['protected_data']['expires_at'] = int(data['protected_data']['expires_at'])
        del data['jwt_token']

        return render_template('general/index.html', **data)


@general_bp.route('/loadkey', methods=['GET', 'POST'])
def loadkey():
    if request.method == 'POST':
        f = request.files['generated_key']
        f.save(os.path.join(basedir, 'generated_key.json'))
        with open('generated_key.json', 'r') as f:
            init(json.load(f))
        return redirect(url_for('general_bp.index'))

    if request.method == 'GET':
        filepath = os.path.join(basedir, 'generated_key.json')
        key_exists = os.path.exists(filepath)

        return render_template('general/loadkey.html', key_exists=key_exists)
