"""
Main blueprint.
"""
import os
import json
from datetime import date
import pathlib
import jwt
import logging
from flask import Blueprint, redirect, render_template, request, url_for, abort, flash
from service.tb import init, init_dashboard
from service.tb.user import (
                            get_user_activation_link, update_user, update_password,
                            create_tenant_admin, default_user_settings)
from service.tb.tenant_profile import get_tenant_profile
from service.tb.tenant import get_tenant, update_tenant, get_tenant_admins_by_tenant_id
from models import TenantProfile, Tenant, TenantAdmin
from database import db
from exceptions import CubaBaseException, UserActivatedException
from general.forms import tenant_form, tenant_admin_form, reset_password_form, add_tenant_admin

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

        try:
            # Get the key file and redirect if does not exist
            filepath = os.path.join(basedir, 'generated_key.json')
            if not os.path.exists(filepath):
                return redirect(url_for('general_bp.loadkey'))

            key = json.load(open(filepath))

            # Get tenant profile id and fetch tenant profile data from Cuba
            try:
                tenant_profile = db.session.scalar(db.select(TenantProfile))
                data['tenant_profile'] = get_tenant_profile(str(tenant_profile.id))
            except AttributeError as exception:
                logging.exception(f'Aception occured: {exception}')
                flash('Профиль владельца не найден', 'error')

            # Get tenant id and fetch tenant data from Cuba
            try:
                tenant = db.session.scalar(db.select(Tenant))
                data['tenant'] = get_tenant(str(tenant.id))
            except AttributeError as exception:
                logging.exception(f'Aception occured: {exception}')
                flash('Аккаунт владельца не найден', 'error')

            # Get all admins and corresponding activation links from Cuba
            if tenant:
                admins = get_tenant_admins_by_tenant_id(tenant.id, page=0)
                data['admins'] = []
                for admin in admins:
                    admin.admin_form = tenant_admin_form.TenantAdminForm()
                    try:
                        admin.activation_url = get_user_activation_link(admin.id)[2:-1]
                    except UserActivatedException:
                        pass
                    data['admins'].append(admin)
                    # init_dashboard(admin.id)
        except CubaBaseException as exception:
            flash(str(exception), 'error')

        # Add miscellaneous data in context
        data['tenant_form'] = tenant_form.TenantForm()
        data['protected_data'] = jwt.decode(key.get('jwt_token'), options={"verify_signature": False})
        data['license_status'] = date.today() < date.fromtimestamp(data['protected_data']['expires_at'])

        return render_template('general/index.html', **data)


@general_bp.route('/admins/<int:page>', methods=['GET', 'POST'])
def admins(page):
    data = {}

    try:
        # Get the key file and redirect if does not exist
        filepath = os.path.join(basedir, 'generated_key.json')
        if not os.path.exists(filepath):
            return redirect(url_for('general_bp.loadkey'))

        key = json.load(open(filepath))

        # Get tenant id and fetch tenant data from Cuba
        try:
            tenant = db.session.scalar(db.select(Tenant))
            data['tenant'] = get_tenant(str(tenant.id))
        except AttributeError as exception:
            logging.exception(f'Aception occured: {exception}')
            flash('Профиль владельца не найден', 'error')

        # Get all admin ids and fetch all admins data and corresponding activation links from Cuba
        if tenant:
            admins = get_tenant_admins_by_tenant_id(tenant.id, page=0)
            data['admins'] = []
            for admin in admins:
                admin.admin_form = tenant_admin_form.TenantAdminForm()
                try:
                    admin.activation_url = get_user_activation_link(admin.id)[2:-1]
                except UserActivatedException:
                    pass
                data['admins'].append(admin)
    except CubaBaseException as exception:
        flash(str(exception), 'error')

    # Add miscellaneous data in context
    data['password_reset_form'] = reset_password_form.ResetPasswordForm()
    data['add_tenant_admin_form'] = add_tenant_admin.AddTenantAdminForm()
    data['tenant_form'] = tenant_form.TenantForm()
    data['protected_data'] = jwt.decode(key.get('jwt_token'), options={"verify_signature": False})
    data['license_status'] = date.today() < date.fromtimestamp(data['protected_data']['expires_at'])

    return render_template('general/admins.html', **data)


@general_bp.route('/update_tenant', methods=['POST'])
def post_tenant():
    # Update tenant
    form = tenant_form.TenantForm()

    # TODO: handle form invalid
    if form.validate_on_submit():
        try:
            update_tenant(tenant_id=form.data.pop('tenant_id'), data=form.data)
        except CubaBaseException as exception:
            flash(str(exception), 'error')

    return redirect(url_for('general_bp.index'))


@general_bp.route('/update_admin', methods=['POST'])
def post_admin():
    # Update tenant admin
    form = tenant_admin_form.TenantAdminForm()

    # TODO: handle form invalid
    if form.validate_on_submit():
        try:
            update_user(user_id=form.data.pop('admin_id'), data=form.data)
        except CubaBaseException as exception:
            flash(str(exception), 'error')
    else:
        return redirect(url_for('general_bp.post_admin'))

    return redirect(url_for('general_bp.index'))


@general_bp.route('/reset_password', methods=['POST'])
def reset_password():
    form = reset_password_form.ResetPasswordForm()

    if form.validate_on_submit():
        # Here goes the logic
        try:
            default_user_settings()
            update_password(form.data['password1'], admin_id=form.data['admin_id'])
        except CubaBaseException as exception:
            flash(str(exception), 'error')
    else:
        return redirect(url_for('general_bp.admins', page=1))

    return redirect(url_for('general_bp.admins', page=1))


@general_bp.route('/add_admin', methods=['POST'])
def add_admin():
    form = add_tenant_admin.AddTenantAdminForm()

    if form.validate_on_submit():
        tenant = db.session.scalar(db.select(Tenant))
        if not tenant:
            logging.error('Tenant not found')
            flash('Владелец не найден')
            return redirect(url_for('general_bp.admins', page=1))

        try:
            create_tenant_admin(
                tenant.id,
                first_name=form.data['first_name'],
                last_name=form.data['last_name'],
                email=form.data['email'],
                phone=form.data['phone']
            )
        except CubaBaseException as exception:
            flash(str(exception), 'error')

    return redirect(url_for('general_bp.admins', page=1))


@general_bp.route('/loadkey', methods=['GET', 'POST'])
def loadkey():
    if request.method == 'POST':
        # There should be a generated_key file in POST request
        f = request.files['generated_key']
        f.save(os.path.join(basedir, 'generated_key.json'))
        p = default_user_settings()
        print(p)
        with open('generated_key.json', 'r') as f:

            # Initiate Cuba with the key
            try:
                p = default_user_settings()
                print(p)
                result = init(json.load(f))
            except CubaBaseException as exception:
                flash(str(exception), 'error')
                return redirect(url_for('general_bp.loadkey'))

            tenant_profile, tenant, tenant_admin, token = result
            # Save models IDs after initialization
            tenant_profile_model = TenantProfile(id=tenant_profile.id.id)
            tenant_model = Tenant(id=tenant.id.id)
            tenant_admin_model = TenantAdmin(id=tenant_admin.id.id)
            print(token.token)
            print(token.refresh_token)
            init_dashboard(token.token, token.refresh_token)
            db.session.add_all([tenant_profile_model, tenant_model, tenant_admin_model])
            db.session.commit()

        return redirect(url_for('general_bp.index', open_tab=True))

    if request.method == 'GET':
        filepath = os.path.join(basedir, 'generated_key.json')
        key_exists = os.path.exists(filepath)

        return render_template('general/loadkey.html', key_exists=key_exists)


@general_bp.route('/asd', methods=['GET'])
def delete():
    try:
        # Delete records from TenantProfile table
        TenantProfile.query.delete()
        # Delete records from Tenant table
        Tenant.query.delete()
        # Delete records from TenantAdmin table
        TenantAdmin.query.delete()
        db.session.commit()
        return "All forms and data deleted successfully"
    except Exception as e:
        db.session.rollback()
        abort(500, str(e))
