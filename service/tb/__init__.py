"""
Module for Cuba API.
"""
import logging

import jwt
from tb_rest_client.rest_client_ce import *

from tb_rest_client.rest import ApiException


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


# ThingsBoard REST API URL
url = "http://localhost:80"

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
            
            return tenant_profile, tenant, user

        except ApiException as e:
            logging.exception(e)
