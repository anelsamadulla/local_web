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
    DeviceProfileData
)
from tb_rest_client.rest import ApiException
from exceptions import NoLicenseException, LicenseNotValidException
import requests  # noqa

basedir = pathlib.Path(__file__).parent.parent.parent.resolve()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# ThingsBoard REST API URL
url = "http://192.168.11.93:80"

# Default Tenant Administrator credentials
username = "sysadmin@thingsboard.org"
password = "654321"


# TODO: Обернуть этим декоратором все функции, которые обращаются к REST API.
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
                    jwt.decode(key['jwt_token'], key=jwt_settings.token_signing_key)

                except jwt.exceptions.DecodeError as exception:
                    logging.error(f'Error decoding license {exception}')
                    raise LicenseNotValidException('Лицензия недействительна.')
            except ApiException as e:
                logging.exception(e)

        return api_func(args, **kwargs)

    return wrapper


def init(data):

    with RestClientCE(base_url=url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            try:
                jwt_settings = rest_client.get_jwt_setting()
                data['protected_data'] = jwt.decode(data['jwt_token'], key=jwt_settings.token_signing_key)
            except jwt.exceptions.DecodeError as exception:
                logging.error(f'Error decoding license {exception}')
                return exception

            tenant_profile = TenantProfile(
                name=f'Профайл {data["company"]}',
                profile_data={
                    'configuration': {
                        "type": "DEFAULT",
                        "maxDevices": data['protected_data']['devices'],
                    }
                }
            )

            tenant_profile = rest_client.save_tenant_profile(tenant_profile)

            if tenant_profile:
                tenant = Tenant(
                    title=data['company'],
                    region=data.get('region', ''),
                    tenant_profile_id=tenant_profile.id,
                    country=data.get('country', ''),
                    state=data.get('state', ''),
                    city=data.get('city', ''),
                    address=data.get('address', ''),
                    zip=data.get('zip', ''),
                    email=data.get('email', 'email@email.com')
                )

                tenant = rest_client.save_tenant(tenant)

                user = User(
                    tenant_id=tenant.id,
                    email=data['issued_for'].get('email', 'tenantAdmin@gmail.com'),
                    authority='TENANT_ADMIN',
                    first_name=data['issued_for']['fname'],
                    last_name=data['issued_for']['lname'],
                    phone=data['issued_for'].get('phone', '77777777777'),
                )

                user = rest_client.save_user(user, send_activation_mail=False)

                admin_token = rest_client.get_user_token(user_id=user.id)

                # Здесь возвращает {'refresh_token': , 'scope': , 'token': }
                print(jwt.decode(admin_token.token, options={"verify_signature": False}))

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

            # logging.info(" Device profile was created:\n%r\n", device_profile)

            # Create and save devices
            devices = []
            for i in range(1, 4):
                device_name = f"camera{i}"
                device = Device(name=device_name, device_profile_id=device_profile.id)
                device = rest_client.save_device(device)
                device_id = rest_client.get_device_by_id(device_id=device.id.id)
                devices.append(device_id)
                # logging.info(f"Device {device_id} was created:\n%r\n", device_id)

            # Save the list of device IDs to a text file
            entity_list = []
            for device in devices:
                entity_list.append(str(device.id.id))

            # Load dashboard configuration from JSON file
            config_file_path2 = os.path.join(basedir, 'default_dashboard.json')
            with open(config_file_path2, 'r') as config_file:
                dashboard_config = json.load(config_file)

                # Update the configuration with the new device IDs under the "Example_cameras" alias
                # Convert the list of device IDs to a JSON-formatted string
                entity_list_json = json.dumps(entity_list)
                # Update the entityList with the JSON-formatted string
                dashboard_config["configuration"]["entityAliases"]["1b22ed84-17fd-7197-96f3-bd0778a3daa2"]["filter"]["entityList"] = entity_list_json  # noqa

                dashboard = Dashboard(
                        name=dashboard_config["name"],
                        title=dashboard_config["title"],
                        configuration=dashboard_config["configuration"]
                    )

                dashboard = rest_client.save_dashboard(dashboard)
                logging.info("Dashboard was created:\n\n")

            # print(dashboard.to_str())

        except ApiException as e:
            logging.exception(e)
