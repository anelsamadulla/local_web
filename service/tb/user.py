from tb_rest_client.rest_client_ce import (
    RestClientCE, ResetPasswordRequest, UserId, ChangePasswordRequest,
    User
)
from tb_rest_client.rest import ApiException

from . import username, password, url, logging
from .tenant import get_tenant
from exceptions import UserActivatedException
import json


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


def get_user(user_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_user_by_id(user_id)

        except ApiException as e:
            if e.body['status'] == 400:
                raise UserActivatedException
            logging.exception(e)


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


def update_password(new_password, admin_id):
    with RestClientCE(url) as rest_client:
        try:
            pass
            # rest_client.token_login(token.token, token.refresh_token)
            # rest_client.get_token()
            # user = rest_client.get_user()
            # print(rest_client.get_user_password_policy())
            # print(rest_client.get_user_settings())
            # print(rest_client.getsett)
            # print(user.discriminator)
            # print(rest_client.get_user_settings())
            # print('ACTIVATION', rest_client.get_activation_link(UserId(id=admin_id, entity_type='USER')))
            # token = rest_client.get_user_token(UserId(id=admin_id, entity_type='USER'))
            # user = rest_client.get_user_by_id(UserId(id=admin_id, entity_type='USER'))
            # print('USER', user)
            # print('TOKEN', token)
            # rest_client.get_user_password_policy()
            # user.authority
            # result = rest_client.set_user_credentials_enabled(user.id, True)
            # result = rest_client.reset_password(ResetPasswordRequest(token.refresh_token))
            # print(result)
        except ApiException as e:
            logging.exception(e)
