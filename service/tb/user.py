from tb_rest_client.rest_client_ce import (
    RestClientCE, UserId, User
)
from tb_rest_client.rest import ApiException

from . import username, password, url, logging, check_credentials
from .tenant import get_tenant
from exceptions import UserActivatedException
import json
import bcrypt
import psycopg2


@check_credentials
def get_user_activation_link(user_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_activation_link(user_id=user_id)

        except ApiException as e:
            error_dict = json.loads(e.body)
            if error_dict['status'] == 400:
                raise UserActivatedException
            logging.exception(e)


@check_credentials
def get_user(user_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_user_by_id(user_id)

        except ApiException as e:
            if e.body['status'] == 400:
                raise UserActivatedException
            logging.exception(e)


@check_credentials
def update_user(user_id, data):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            user = rest_client.get_user_by_id(user_id)
            user.first_name = data['first_name']
            user.last_name = data['last_name']

            return rest_client.save_user(user)

        except ApiException as e:
            logging.exception(e)


@check_credentials
def create_tenant_admin(tenant_id, **kwargs):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            tenant = get_tenant(tenant_id)

            user = User(
                tenant_id=tenant.id,
                authority='TENANT_ADMIN',
                **kwargs
            )

            user = rest_client.save_user(user, False)

            return True

        except ApiException as e:
            logging.exception(e)


def get_user_token(admin_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            token = rest_client.get_user_token(UserId(id=admin_id, entity_type='USER'))
            return token

        except ApiException as e:
            logging.exception(e)


@check_credentials
def update_password(new_password, admin_id):
    try:
        hashed = bcrypt.hashpw(
            new_password.encode(),
            bcrypt.gensalt(10, b'2a')
        )

        print('HASHED', hashed)
        conn = psycopg2.connect(
            database="thingsboard",
            user="postgres",
            host="localhost",
            password="postgres",
            port=5432
        )
        cur = conn.cursor()
        cur.execute(
            f"UPDATE user_credentials SET password = '{hashed.decode()}' WHERE user_id = '{admin_id}';"
        )
        conn.commit()

    except Exception as e:
        logging.exception(e)

    finally:
        cur.close()
        conn.close()


@check_credentials
def set_user_credentials_enabled(user_id: str, enabled: bool):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            rest_client.set_user_credentials_enabled(UserId(user_id, "USER"), enabled)
        except ApiException as e:
            logging.exception(e)


@check_credentials
def delete_user(user_id: str):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            rest_client.delete_user(UserId(user_id, 'USER'))
        except ApiException as e:
            logging.exception(e)
