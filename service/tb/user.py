from tb_rest_client.rest_client_ce import (
    RestClientCE, ResetPasswordRequest, UserId,
    User
)
from tb_rest_client.rest import ApiException

from . import username, password, url, logging, check_credentials
from .tenant import get_tenant
from exceptions import UserActivatedException
import json


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
    with RestClientCE(url) as rest_client:
        try:
            user_info = get_user(admin_id)
            rest_client.login(username=user_info.email, password="dhacda")          
        except ApiException as e:
            # Check if the ApiException contains information about expired credentials
            if e.status == 401 and 'resetToken' in e.body:
                reset_token = e.body['resetToken']
                # Handle the reset token as needed
                print("Reset Token:", reset_token)
                change_password_request = ResetPasswordRequest(reset_token=reset_token, new_password=new_password)
                response = rest_client.change_password(change_password_request)
                # return rest_client.save_user(User(id=UserId(id=admin_id)), send_activation_mail=False)
                if response.status == 200:
                    print("Password reset successful.")
                    return True
                else:
                    print("Password reset failed.")
                    return False
            else:
                # Handle other ApiException cases if needed
                logging.exception(e)
                

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
