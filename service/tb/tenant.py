from tb_rest_client.rest_client_ce import RestClientCE, TenantId, Tenant
from tb_rest_client.rest import ApiException

from . import username, password, url, logging


def get_tenant(tenant_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_tenant_by_id(tenant_id)
            
        except ApiException as e:
            logging.exception(e)
            
            
def update_tenant(tenant_id: str, data):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)
            
            tenant = rest_client.get_tenant_by_id(tenant_id)
            tenant.country = data['country']
            tenant.state = data['state']
            tenant.city = data['city']
            tenant.address = data['address']
            tenant.address2 = data['address2']
            tenant.zip = data['zip_code']
            tenant.phone = data['phone']
            
            return rest_client.save_tenant(tenant)
            
        except ApiException as e:
            logging.exception(e)
