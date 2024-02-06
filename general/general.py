"""
Main blueprint.
"""
import os
import json
from datetime import date
import pathlib

import jwt
from flask import Blueprint, redirect, render_template, request, url_for
from service.tb import init
from service.tb.user import get_user_activation_link, get_user
from service.tb.tenant_profile import get_tenant_profile
from service.tb.tenant import get_tenant
from models import TenantProfile, Tenant, TenantAdmin
from database import db
from exceptions import UserActivatedException


basedir = pathlib.Path(__file__).parent.parent.resolve()


general_bp = Blueprint(
    'general_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/assets'
)


@general_bp.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        data = {}

        # Get the key file and redirect if does not exist
        filepath = os.path.join(basedir, 'generated_key.json')
        if not os.path.exists(filepath):
            return redirect(url_for('general_bp.loadkey'))
        
        key = json.load(open(filepath))
        
        # Get tenant profile id and fetch tenant profile data from Cuba
        tenant_profile = db.session.scalar(db.select(TenantProfile))
        data['tenant_profile'] = get_tenant_profile(str(tenant_profile.id))

        # Get tenant id and fetch tenant data from Cuba
        tenant = db.session.scalar(db.select(Tenant))
        data['tenant'] = get_tenant(str(tenant.id))
            
        # Get all admin ids and fetch all admins data and corresponding activation links from Cuba
        admins = db.session.scalars(db.select(TenantAdmin)).all()
        data['admins'] = []
        for admin in admins:
            user = get_user(admin.id)
            try:
                user.activation_url = get_user_activation_link(admin.id)[2:-1]
            except UserActivatedException:
                pass
            data['admins'].append(user)
        print(data['admins'])
            
        data['protected_data'] = jwt.decode(key['jwt_token'], options={"verify_signature": False})
        data['license_status'] = date.today() < date.fromtimestamp(data['protected_data']['expires_at'])

        return render_template('general/index.html', **data)


@general_bp.route('/loadkey', methods=['GET', 'POST'])
def loadkey():
    if request.method == 'POST':
        f = request.files['generated_key']
        f.save(os.path.join(basedir, 'generated_key.json'))

        with open('generated_key.json', 'r') as f:
            tenant_profile, tenant, tenant_admin = init(json.load(f))

            tenant_profile_model = TenantProfile(id=tenant_profile.id.id)
            tenant_model = Tenant(id=tenant.id.id)
            tenant_admin_model = TenantAdmin(id=tenant_admin.id.id)
            db.session.add_all([tenant_profile_model, tenant_model, tenant_admin_model])
            db.session.commit()
                    
        return redirect(url_for('general_bp.index'))

    if request.method == 'GET':
        filepath = os.path.join(basedir, 'generated_key.json')
        key_exists = os.path.exists(filepath)

        return render_template('general/loadkey.html', key_exists=key_exists)
    
    
@general_bp.route('/asd', methods=['GET'])
def delete():
    tenant_profile = db.session.scalar(db.select(TenantProfile))
    db.session.delete(tenant_profile)
    db.session.commit()
    
    tenant = db.session.scalar(db.select(Tenant))
    db.session.delete(tenant)
    db.session.commit()
    
    admins = db.session.scalars(db.select(TenantAdmin)).all()
    for admin in admins:
        db.session.delete(admin)
    db.session.commit()
