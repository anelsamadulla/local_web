"""
Module for Cuba API.
"""
import logging
import os, pathlib
import json 
import jwt
from tb_rest_client.rest_client_ce import *
from tb_rest_client.rest_client_ce import RestClientCE
from tb_rest_client.rest import ApiException
import requests

basedir = pathlib.Path(__file__).parent.parent.parent.resolve()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# ThingsBoard REST API URL
url = "http://192.168.11.93:80"

# Default Tenant Administrator credentials
username = "sysadmin@thingsboard.org"
password = "sysadmin"

def init(data):
    print(data)
    data['protected_data'] = jwt.decode(data['jwt_token'], options={"verify_signature": False})
    with RestClientCE(base_url=url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            
            tenant_profile = TenantProfile(name=f'Профайл {data["company"]}', 
                        profile_data={
                            'configuration': {
                                "type": "DEFAULT",
                                "maxDevices": data['protected_data']['devices'],
                            }
                        })
            
            tenant_profile = rest_client.save_tenant_profile(tenant_profile)

            if tenant_profile:
                tenant = Tenant(
                    title=data['company'],
                    region=data.get('region', 'Азия'),
                    tenant_profile_id=tenant_profile.id,
                    country=data.get('country', 'Казахстан'),
                    state=data.get('state', 'Астана'),
                    city=data.get('city', 'Астана'),
                    address=data.get('address', 'Адрес'),
                    zip=data.get('zip', '010000'),
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
        
                # Initialize dashboard and device profile
                # device_profile, dashboard = init_dashboard(tenant.id)

                return tenant_profile, tenant, user
            
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
        
def init_dashboard(tenant_username, tenant_password):

    with RestClientCE(base_url=url) as rest_client:
        try:
            rest_client.login(username=tenant_username, password=tenant_password)
            #default_asset_profile_id = rest_client.get_default_asset_profile_info().id
            #asset = Asset(name="Building 1", asset_profile_id=default_asset_profile_id)
            # Load device profile from JSON file
            config_file_path1 = os.path.join(basedir, 'example_camera_profile.json')
            with open(config_file_path1, 'r') as config_file:
                device_profile_data = json.load(config_file)
            
            # Create and save device profile
            # default_device_profile_id = rest_client.get_default_device_profile_info().id
            # device_profile = DeviceProfile(device_profile_id = default_device_profile_id, name=device_profile_data["name"], profile_data=device_profile_data)
            # Create the DeviceProfile object
            device_profile = DeviceProfile(tenant_id=tenant_id, 
                                            name=device_profile_data["name"],
                                            description=device_profile_data["description"],
                                            profile_data=DeviceProfileData(configuration={"type": "DEFAULT"},
                                                                          transport_configuration={"type": "DEFAULT"})
                                            )
                                                                    
                                            # provision_device_key=device_profile_data["provisionDeviceKey"],
                                            # firmware_id=device_profile_data["firmwareId"],
                                            # software_id=device_profile_data["softwareId"],
                                            # default_edge_rule_chain_id=device_profile_data["defaultEdgeRuleChainId"],
                                            # default=device_profile_data["default"]
            device_profile = rest_client.save_device_profile(device_profile)

            logging.info(" Device profile was created:\n%r\n", device_profile)

            device = Device(name="camera1", device_profile_id=device_profile.id)
            device = rest_client.save_device(device)

            device = Device(name="camera2", device_profile_id=device_profile.id)
            device = rest_client.save_device(device)

            device = Device(name="camera3", device_profile_id=device_profile.id)
            device = rest_client.save_device(device)

            logging.info(" Device was created:\n%r\n", device)

           # Load dashboard configuration from JSON file
            config_file_path2 = os.path.join(basedir, 'default_dashboard.json')
            with open(config_file_path2, 'r') as config_file:
                dashboard_config = json.load(config_file)
                dashboard = Dashboard(
                    name=dashboard_config["title"],
                    title=dashboard_config["title"],
                    configuration=dashboard_config["configuration"]
                )
                
            dashboard = rest_client.save_dashboard(dashboard)

            logging.info("Dashboard was created:\n%r\n", relation)
            # Creating relations from device to asset
            relation = EntityRelation(_from=device.id, to=dashboard.id, type="Contains")
            rest_client.save_relation(relation)

            logging.info(" Relation was created:\n%r\n", relation)

            return device_profile, dashboard 

        except ApiException as e:
            logging.exception(e)
