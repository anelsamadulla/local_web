from tb_rest_client.rest_client_ce import RestClientCE
from tb_rest_client.rest import ApiException

from . import username, password, url, logging, check_credentials


@check_credentials
def get_tenant(tenant_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_tenant_by_id(tenant_id)

        except ApiException as e:
            logging.exception(e)


@check_credentials
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


@check_credentials
def get_tenant_admins_by_tenant_id(tenant_id, page, page_size=999):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            admins = rest_client.get_tenant_admins(tenant_id=tenant_id, page_size=page_size, page=page)

            return (admins.data, admins.total_pages, admins.has_next)

        except ApiException as e:
            logging.exception(e)
