"""
Module for Cuba API.
"""
import logging
import os
import pathlib
import json
import jwt
from tb_rest_client.rest_client_ce import (
    RestClientCE, TenantProfile, Tenant, User, DeviceProfile, Device, Dashboard,
    DeviceProfileData, TenantProfileId, TenantId
)
from tb_rest_client.rest import ApiException
from exceptions import NoLicenseException, LicenseNotValidException, RestApiNotAvailableexception
import requests  # noqa
from database import db
from models import TenantProfile as TenantProfileModel, Tenant as TenantModel
from ast import literal_eval

basedir = pathlib.Path(__file__).parent.parent.parent.resolve()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# ThingsBoard REST API URL
url = "localhost:8080"

# Default Tenant Administrator credentials
username = "sysadmin@thingsboard.org"
password = "sysadmin"


def check_credentials(api_func):
    """Check if license is valid"""
    def wrapper(*args, **kwargs):
        # Get the key file and raise if does not exist.
        filepath = os.path.join(basedir, 'generated_key.json')
        if not os.path.exists(filepath):
            raise NoLicenseException('Лицензия не найдена.')

        # Open license and validate it.
        key = json.load(open(filepath))
        with RestClientCE(base_url=url) as rest_client:
            try:
                rest_client.login(username=username, password=password)
                try:
                    jwt_settings = rest_client.get_jwt_setting()
                    jwt.decode(
                        key['jwt_token'],
                        key=jwt_settings.token_signing_key,
                        algorithms=['HS256']
                    )

                except jwt.exceptions.DecodeError as exception:
                    logging.error(f'Error decoding license {exception}')
                    raise LicenseNotValidException('Лицензия недействительна.')
            except ApiException as e:
                logging.exception(e)
                raise RestApiNotAvailableexception('Не удалось подключиться к платформе')

        return api_func(*args, **kwargs)

    return wrapper


def init(data):

    with RestClientCE(base_url=url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            try:
                jwt_settings = rest_client.get_jwt_setting()
                data['protected_data'] = jwt.decode(
                    data['jwt_token'],
                    key=jwt_settings.token_signing_key,
                    algorithms=['HS256']
                )
            except jwt.exceptions.DecodeError as exception:
                logging.error(f'Error decoding license {exception}')
                raise LicenseNotValidException('Лицензия недействительна.')
            except KeyError as exception:
                logging.exception(f'Error decoding license {exception}')
                raise LicenseNotValidException('Лицензия недействительна.')

            tenant_profile = TenantProfile(
                name=f'Профайл {data["company"]}',
                profile_data={
                    'configuration': {
                        "type": "DEFAULT",
                        "maxDevices": data['protected_data']['devices'],
                    }
                }
            )

            try:
                tenant_profile = rest_client.save_tenant_profile(tenant_profile)
            except ApiException as e:
                error_body = literal_eval(e.body.decode("UTF-8"))
                if error_body["errorCode"] == 31:
                    tenant_profile_record = db.session.scalar(db.select(TenantProfileModel))
                    tenant_profile = rest_client.get_tenant_profile_by_id(
                        TenantProfileId(tenant_profile_record.id,
                                        'TENANT_PROFILE'))
                    tenant_profile.profile_data.configuration['maxDevices'] = data['protected_data']['devices']
                    tenant_profile = rest_client.save_tenant_profile(tenant_profile)
                else:
                    logging.exception(f'Unhandled exception: {e}')

            if tenant_profile:

                # try:
                tenant_record = db.session.scalar(db.select(TenantModel))
                if tenant_record:

                    tenant = rest_client.get_tenant_by_id(TenantId(tenant_record.id, 'TENANT'))
                    if tenant.title != data.get('company'):
                        tenant.title = data.get('company', tenant.title)
                        tenant.region = data.get('region', tenant.region)
                        tenant.country = data.get('country', tenant.country)
                        tenant.state = data.get('state', tenant.state)
                        tenant.city = data.get('city', tenant.city)
                        tenant.address = data.get('address', tenant.address)
                        tenant.zip = data.get('zip', tenant.zip)
                        tenant.email = data.get('email', tenant.email)
                else:
                    tenant = Tenant(
                        title=data['company'],
                        region=data.get('region', ''),
                        tenant_profile_id=tenant_profile.id,
                        country=data.get('country', ''),
                        state=data.get('state', ''),
                        city=data.get('city', ''),
                        address=data.get('address', ''),
                        zip=data.get('zip', ''),
                        email=data.get('email', '')
                    )
                # except ApiException as e:
                #     error_body = literal_eval(e.body.decode("UTF-8"))
                #     if error_body['errorCode'] == 32:
                #         print('TENANT', tenant)
                #         tenant = Tenant(
                #             title=data['company'],
                #             region=data.get('region', ''),
                #             tenant_profile_id=tenant_profile.id,
                #             country=data.get('country', ''),
                #             state=data.get('state', ''),
                #             city=data.get('city', ''),
                #             address=data.get('address', ''),
                #             zip=data.get('zip', ''),
                #             email=data.get('email', '')
                #         )
                #     else:
                #         logging.exception(f'Unhandled exception: {e}')

                tenant = rest_client.save_tenant(tenant)

                try:
                    user = User(
                        tenant_id=tenant.id,
                        email=data['issued_for']['email'],
                        authority='TENANT_ADMIN',
                        first_name=data['issued_for']['fname'],
                        last_name=data['issued_for']['lname'],
                        phone=data['issued_for']['phone'],
                    )

                    user = rest_client.save_user(user, send_activation_mail=False)
                except ApiException as e:
                    error_body = literal_eval(e.body.decode("UTF-8"))
                    if error_body["errorCode"] == 31:
                        # User already exists we don't have to do anything else
                        return tenant_profile, tenant, None, None
                    else:
                        logging.exception(f'Unhandled exception: {e}')

                admin_token = rest_client.get_user_token(user_id=user.id)

                # Здесь возвращает {'refresh_token': , 'scope': , 'token': }
                # print(jwt.decode(admin_token.token, options={"verify_signature": False}))

                admin_token.refresh_token
                # rest_client.check_activate_token(user_token)

                # Initialize dashboard and device profile
                # device_profile, dashboard = init_dashboard(tenant.id)

                return tenant_profile, tenant, user, admin_token

            else:
                # Handle the case when tenant profile creation fails
                error_message = "Failed to create tenant profile"
                # You can log the error, display a message to the user, or redirect to an error page
                logging.error(error_message)
                # Return None or raise an exception to indicate failure
                return None

        except ApiException as e:
            logging.exception(e)
            # Handle the exception and provide appropriate feedback
            error_message = "An error occurred during initialization"
            # You can log the error, display a message to the user, or redirect to an error page
            logging.error(error_message)
            # Return None or raise an exception to indicate failure
            return None


def init_dashboard(token, refresh_token):

    with RestClientCE(base_url=url) as rest_client:
        try:
            rest_client.token_login(token=token, refresh_token=refresh_token)

            # Load device profile from JSON file
            config_file_path1 = os.path.join(basedir, 'example_camera_profile.json')
            with open(config_file_path1, 'r') as config_file:
                device_profile_data = json.load(config_file)

            # Create the DeviceProfile object
            device_profile = DeviceProfile(
                name=device_profile_data["name"],
                type='DEFAULT',
                transport_type='DEFAULT',
                description=device_profile_data["description"],
                profile_data=DeviceProfileData(
                    configuration={"type": "DEFAULT"},
                    transport_configuration={"type": "DEFAULT"}),
                provision_device_key=device_profile_data["provisionDeviceKey"],
                firmware_id=device_profile_data["firmwareId"],
                software_id=device_profile_data["softwareId"],
                default_edge_rule_chain_id=device_profile_data["defaultEdgeRuleChainId"],
                default=device_profile_data["default"]
            )
            device_profile = rest_client.save_device_profile(device_profile)

            # Create and save devices
            devices = []
            for i in range(1, 4):
                device_name = f"Камера {i}"
                device = Device(name=device_name, device_profile_id=device_profile.id)
                device = rest_client.save_device(device)
                devices.append(device)

            coords = (
                (51.156751, 71.430434),
                (51.147074, 71.422338),
                (51.156940, 71.411691),
            )

            for i in range(0, 3):
                rest_client.telemetry_controller.save_device_attributes_using_post(
                    device_id=devices[i].id.id,
                    scope='SERVER_SCOPE',
                    body={
                        "latitude": coords[i][0],
                        "longitude": coords[i][1],
                        "place": devices[i].name
                    }
                )

            # Load existing dashboard configuration
            config_file_path2 = os.path.join(basedir, 'demo_cameras_dashboard.json')
            with open(config_file_path2, 'r') as config_file:
                dashboard_config = json.load(config_file)

            # Create a new dashboard object with the updated configuration
            dashboard = Dashboard(
                name=dashboard_config["name"],
                title=dashboard_config["title"],
                configuration=dashboard_config["configuration"]
            )

            # Save the updated dashboard
            dashboard = rest_client.save_dashboard(dashboard)
            logging.info("Dashboard was created:\n%r\n", dashboard)
            # print(dashboard.to_str())

        except ApiException as e:
            logging.exception(e)
