import json
import requests
import vps_config as cfg

# This module has an methods which helps to fetch data from api


#Static URL
URL = 'https://api.vultr.com/v2/'
headers = {'Authorization': 'Bearer {}'.format(cfg.api_keys['VULTR_KEY']),
            'Content-Type': 'application/json'}
class Instance:
    """ Class describes VPS instance properties and methods """
    def __init__(self,id,label):
        self.id = id
        self.label = label

    @staticmethod
    def list_instances() -> list:
        """ Lists available instances """
        response = requests.get(URL +'instances', headers=headers)
        data = json.loads(response.text)
        instances = []
        for instance in data['instances']:
            instance = {
                'id': instance['id'],
                'label':instance['label'],
                'os':instance['os'],
                'ram':instance['ram'],
                'disk':instance['disk'],
                'main_ip':instance['main_ip'],
                'vcpu_count':instance['vcpu_count'],
                'region':instance['region'],
                'server_status':instance['server_status'],
                'power_status':instance['power_status']
            }
            instances.append(instance)
        return instances

    @staticmethod
    def get_instance_bandwidth(instance_id):
        """ Returns instance bandwidth  """
        response = requests.get(URL + f'instances/{instance_id}/bandwidth',headers=headers)
        bandwidth = json.loads(response.text)
        return bandwidth

# TODO: Make human readable text
    def get_instance_info(self , instance_id):
        """ Returns non-formated instance properties """
        response = requests.get(URL + f'instances/{instance_id}', headers=headers)
        data = json.loads(response.text)
        # formatted_data = json.dumps(data.get('instance'), indent=2 ,sort_keys=True)
        # text = 'Here is instance properties \n' + formatted_data
        # newtext = text.replace('"', ' ' , len(text))
        return data
