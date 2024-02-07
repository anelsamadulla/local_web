from tb_rest_client.rest_client_ce import RestClientCE
from tb_rest_client.rest import ApiException

from . import username, password, url, logging
from exceptions import UserActivatedException
import json


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


def get_user(user_id):
    with RestClientCE(url) as rest_client:
        try:
            rest_client.login(username=username, password=password)

            return rest_client.get_user_by_id(user_id)
        
        except ApiException as e:
            if e.body['status'] == 400:
                raise UserActivatedException
            logging.exception(e)
            
            
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
