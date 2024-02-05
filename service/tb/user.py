from tb_rest_client.rest_client_ce import RestClientCE
from tb_rest_client.rest import ApiException

from . import username, password, url, logging


def get_user_activation_link(user_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_activation_link(user_id=user_id)
            
        except ApiException as e:
            print(e)
            logging.exception(e)


def get_user(user_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_user_by_id(user_id)
        
        except ApiException as e:
            logging.exception(e)
