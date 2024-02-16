"""
Main blueprint.
"""
import os
import json, jsonify 
from datetime import date
import pathlib
import jwt
from flask import Blueprint, redirect, render_template, request, url_for
from service.tb import init, init_dashboard
from service.tb.user import get_user_activation_link, update_user
from service.tb.tenant_profile import get_tenant_profile
from service.tb.tenant import get_tenant, update_tenant, get_tenant_admins_by_tenant_id
from models import TenantProfile, Tenant, TenantAdmin
from database import db
from exceptions import UserActivatedException
from general.forms import tenant_form
from general.forms import tenant_admin_form
from service.tb import url
import requests
from requests.exceptions import RequestException

basedir = pathlib.Path(__file__).parent.parent.resolve()

general_bp = Blueprint(
    'general_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/assets'
)

@general_bp.route('/', methods=['GET'])
def index(open_tab=False):
    # Handle GET request
    if request.method == 'GET':
        data = {'open_tab': open_tab}

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

        # Get all admins and corresponding activation links from Cuba
        admins = get_tenant_admins_by_tenant_id(tenant.id, page=0)
        data['admins'] = []
        for admin in admins:
            admin.admin_form = tenant_admin_form.TenantAdminForm()
            try:
                admin.activation_url = get_user_activation_link(admin.id)[2:-1]
            except UserActivatedException:
                pass
            data['admins'].append(admin)

        # Add miscellaneous data in context
        data['tenant_form'] = tenant_form.TenantForm()
        data['protected_data'] = jwt.decode(key['jwt_token'], options={"verify_signature": False})
        data['license_status'] = date.today() < date.fromtimestamp(data['protected_data']['expires_at'])

        return render_template('general/index.html', **data)

@general_bp.route('/admins/<int:page>', methods=['GET'])
def admins(page):
    data = {}

    # Get the key file and redirect if does not exist
    filepath = os.path.join(basedir, 'generated_key.json')
    if not os.path.exists(filepath):
        return redirect(url_for('general_bp.loadkey'))

    key = json.load(open(filepath))

    # Get tenant id and fetch tenant data from Cuba
    tenant = db.session.scalar(db.select(Tenant))
    data['tenant'] = get_tenant(str(tenant.id))

    # Get all admin ids and fetch all admins data and corresponding activation links from Cuba
    admins = get_tenant_admins_by_tenant_id(tenant.id, page=0)
    data['admins'] = []
    for admin in admins:
        admin.admin_form = tenant_admin_form.TenantAdminForm()
        try:
            admin.activation_url = get_user_activation_link(admin.id)[2:-1]
        except UserActivatedException:
            pass
        data['admins'].append(admin)

    # Add miscellaneous data in context
    data['tenant_form'] = tenant_form.TenantForm()
    data['protected_data'] = jwt.decode(key['jwt_token'], options={"verify_signature": False})
    data['license_status'] = date.today() < date.fromtimestamp(data['protected_data']['expires_at'])

    return render_template('general/admins.html', **data)

# Route to handle activation and initialization
@general_bp.route('/activate_admin', methods=['POST'])
def activate_admin():
    data = request.json
    admin_id = data.get('admin_id')
    email = data.get('email')  # Retrieve email from request payload
    new_password = data.get('new_password')
    
    # Call init_dashboard with email, admin_id, and new_password
    init_dashboard(email, new_password)

    return jsonify({'message': 'Admin activated and dashboard initialized successfully'})


@general_bp.route('/update_tenant', methods=['POST'])
def post_tenant():
    # Update tenant
    form = tenant_form.TenantForm()

    if form.validate_on_submit():
        update_tenant(tenant_id=form.data.pop('tenant_id'), data=form.data)

    return redirect(url_for('general_bp.index'))


@general_bp.route('/update_admin', methods=['POST'])
def post_admin():
    # Update tenant admin
    form = tenant_admin_form.TenantAdminForm()

    if form.validate_on_submit():
        update_user(user_id=form.data.pop('admin_id'), data=form.data)

    return redirect(url_for('general_bp.index'))


@general_bp.route('/loadkey', methods=['GET', 'POST'])
def loadkey():
    if request.method == 'POST':
        # There should be a generated_key file in POST request
        f = request.files['generated_key']
        f.save(os.path.join(basedir, 'generated_key.json'))

        with open('generated_key.json', 'r') as f:
            # Initiate Cuba with the key
            tenant_profile, tenant, tenant_admin = init(json.load(f))    
            # Save models IDs after initialization
            tenant_profile_model = TenantProfile(id=tenant_profile.id.id)
            tenant_model = Tenant(id=tenant.id.id)
            tenant_admin_model = TenantAdmin(id=tenant_admin.id.id)
            db.session.add_all([tenant_profile_model, tenant_model, tenant_admin_model])
            db.session.commit()

        return redirect(url_for('general_bp.index', open_tab=True))

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
