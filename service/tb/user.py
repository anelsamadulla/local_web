from tb_rest_client.rest_client_ce import (
    RestClientCE, ResetPasswordRequest, UserId,
    User, SecuritySettings
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


def get_user_security_settings():
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            security_settings = rest_client.get_security_settings()
            return security_settings

        except ApiException as e:
            logging.exception(e)


def get_user_password_policy():
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            password_policy = rest_client.get_user_password_policy()
            return password_policy

        except ApiException as e:
            logging.exception(e)


def save_user_security_settings(password_policy):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            security_settings = rest_client.save_security_settings(SecuritySettings(
                                                                password_policy=password_policy))
            return security_settings

        except ApiException as e:
            logging.exception(e)


def change_password_policy():
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            new_password_policy = rest_client.put_user_settings({
                        'allow_whitespaces': False,
                        'force_user_to_reset_password_if_not_valid': True,
                        'maximum_length': 0,
                        'minimum_digits': 0,
                        'minimum_length': 0,
                        'minimum_lowercase_letters': 0,
                        'minimum_special_characters': 0,
                        'minimum_uppercase_letters': 0,
                        'password_expiration_period_days': -1,
                        'password_reuse_frequency_days': 0}
                    )
            print(new_password_policy)
            return new_password_policy

        except ApiException as e:
            logging.exception(e)


def default_user_settings():
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            new_password_policy = rest_client.put_user_settings({
                        'allow_whitespaces': False,
                        'force_user_to_reset_password_if_not_valid': False,
                        'maximum_length': None,
                        'minimum_digits': None,
                        'minimum_length': None,
                        'minimum_lowercase_letters': None,
                        'minimum_special_characters': None,
                        'minimum_uppercase_letters': None,
                        'password_expiration_period_days': None,
                        'password_reuse_frequency_days': None}
                    )
            new_security_settings = rest_client.save_security_settings(SecuritySettings(
                                                password_policy=new_password_policy,
                                                max_failed_login_attempts=None))
            print(new_password_policy)
            print(new_security_settings)
            return new_password_policy

        except ApiException as e:
            logging.exception(e)


@check_credentials
def update_password(new_password, admin_id):
    with RestClientCE(url) as rest_client:
        try:
            user_info = get_user(admin_id)
            print(user_info)
            password_policy = get_user_password_policy()
            print(password_policy)
            security_settings = get_user_security_settings()
            print(security_settings)
            password_policy = change_password_policy()
            security_settings = save_user_security_settings(password_policy)
            rest_client.login(username=user_info.email, password="dhacda")
            print("\n")
        except ApiException as e:
            print(e)
            # Check if the ApiException contains information about expired credentials
            if e.status == 401 and 'resetToken' in e.body:
                reset_token = e.body['resetToken']
                # Handle the reset token as needed
                print("Reset Token:", reset_token)
                rest_client.check_reset_token(reset_token=reset_token)
                change_password_request = ResetPasswordRequest(reset_token=reset_token, new_password=new_password)
                response = rest_client.change_password(change_password_request)
                # return rest_client.save_user(User(id=UserId(id=admin_id)), send_activation_mail=False)
                if response.status == 200:
                    print("Password reset successful.")
                    default_user_settings()
                    return True
                else:
                    print("Password reset failed.")
                    default_user_settings()
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
