"""
Module for Cuba API.
"""
import logging
import os
import pathlib
import json
import jwt
from tb_rest_client.rest_client_ce import (
    RestClientCE, TenantProfile, Tenant, User, DeviceProfile, Device, Dashboard, EntityRelation
)
from tb_rest_client.rest import ApiException
import requests  # noqa

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

                print(admin_token)  # Здесь возвращает {'refresh_token': , 'scope': , 'token': }

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


def init_dashboard(tenant_username, tenant_password):

    with RestClientCE(base_url=url) as rest_client:
        try:
            # rest_client.is_user_token_access_enabled()
            # password_user = rest_client.get_user_password_policy()
            rest_client.token_login(token=token, refresh_token=refresh_token)
            # rest_client.login(username=email, password=password_user)
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
            device_profile = DeviceProfile(
                                            name=device_profile_data["name"],
                                            type='DEFAULT',
                                            transport_type='DEFAULT',
                                            description=device_profile_data["description"],
                                            profile_data=DeviceProfileData(configuration={"type": "DEFAULT"},
                                                                          transport_configuration={"type": "DEFAULT"}),                      
                                            provision_device_key=device_profile_data["provisionDeviceKey"],
                                            firmware_id=device_profile_data["firmwareId"],
                                            software_id=device_profile_data["softwareId"],
                                            default_edge_rule_chain_id=device_profile_data["defaultEdgeRuleChainId"],
                                            default=device_profile_data["default"]
                                            )
            device_profile = rest_client.save_device_profile(device_profile)

            logging.info(" Device profile was created:\n%r\n", device_profile)

            # device1 = Device(name="camera1", device_profile_id=device_profile.id)
            # device1 = rest_client.save_device(device1)
            # id1 = rest_client.get_device_by_id(device_id=device1.id.id)
            

            # device2 = Device(name="camera2", device_profile_id=device_profile.id)
            # device2 = rest_client.save_device(device2)
            # id2 = rest_client.get_device_by_id(device_id=device2.id.id)

            # device3 = Device(name="camera3", device_profile_id=device_profile.id)
            # device3 = rest_client.save_device(device3)
            # id3 = rest_client.get_device_by_id(device_id=device3.id.id)

            # logging.info(f"Device {id1}, {id2}, {id3} were created:\n%r\n")

        #    # Load dashboard configuration from JSON file
        #     config_file_path2 = os.path.join(basedir, 'default_dashboard.json')
        #     with open(config_file_path2, 'r') as config_file:
        #         dashboard_config = json.load(config_file)
        #         dashboard = Dashboard(
        #             name=dashboard_config["name"],
        #             title=dashboard_config["title"],
        #             configuration=dashboard_config["configuration"]["entityAliases"]
        #         )

        #     dashboard = rest_client.save_dashboard(dashboard)
        #     logging.info("Dashboard was created:\n\n")
            # print(dashboard.to_str())
            
            # rest_client.get_dashboard_info_by_id()
            
            # rel_dashboard_id = rest_client.get_dashboard_by_id(dashboard_id= DashboardId(dashboard.to_str(), 'DASHBOARD'))
            # # Creating relations from device to asset
            # relation = EntityRelation(_from=id1, to=rel_dashboard_id, type="Contains", type_group="COMMON")
            # relation = rest_client.save_relation(relation)
            # logging.info(" Relation was created:\n%r\n", relation) 
            # Create and save devices

            devices = []
            for i in range(1, 4):
                device_name = f"camera{i}"
                device = Device(name=device_name, device_profile_id=device_profile.id)
                device = rest_client.save_device(device)
                device_id = rest_client.get_device_by_id(device_id=device.id.id)
                devices.append(device_id)
                logging.info(f"Device {device_id} was created:\n%r\n", device_id)

            # Save the list of device IDs to a text file
            # entity_list_file_path = os.path.join(basedir, 'entity_list.txt')
            # with open(entity_list_file_path, 'w') as entity_list_file:
            #     for index, device in enumerate(devices):
            #         entity_list_file.write(f'"{device.id.id}"')
            #         if index < len(devices) - 1:
            #             entity_list_file.write(',')
            # logging.info("Entity list saved to entity_list.txt")

            entity_list = []
            for device in devices:
                entity_list.append(str(device.id.id))
            # Load dashboard configuration from JSON file
            config_file_path2 = os.path.join(basedir, 'default_dashboard.json')
            with open(config_file_path2, 'r') as config_file:
                dashboard_config = json.load(config_file)
        
                # dashboard_config["configuration"]["entityAliases"]["1b22ed84-17fd-7197-96f3-bd0778a3daa2"]["filter"]["entityList"] = []
                
                # Update the configuration with the new device IDs under the "Example_cameras" alias
                # dashboard_config["configuration"]["entityAliases"]["1b22ed84-17fd-7197-96f3-bd0778a3daa2"]["filter"]["entityList"] = [d.id for d in devices]
                # Convert the list of device IDs to a JSON-formatted string
                
                entity_list_json = json.dumps(entity_list)
                # Update the entityList with the JSON-formatted string
                dashboard_config["configuration"]["entityAliases"]["1b22ed84-17fd-7197-96f3-bd0778a3daa2"]["filter"]["entityList"] = entity_list_json
                
                dashboard = Dashboard(
                        name=dashboard_config["name"],
                        title=dashboard_config["title"],
                        configuration=dashboard_config["configuration"]
                    )

                dashboard = rest_client.save_dashboard(dashboard)
                logging.info("Dashboard was created:\n\n")

            print(dashboard.to_str())

        except ApiException as e:
            logging.exception(e)
