from tb_rest_client.rest_client_ce import RestClientCE
from tb_rest_client.rest import ApiException

from . import username, password, url, logging, check_credentials


@check_credentials
def get_tenant_profile(tenant_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_tenant_profile_by_id(tenant_id)

        except ApiException as e:
            logging.exception(e)
