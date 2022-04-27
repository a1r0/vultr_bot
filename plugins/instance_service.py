import json
import requests
import vps_config as cfg

URL = 'https://api.vultr.com/v2/'
headers = {'Authorization': 'Bearer {}'.format(cfg.api_keys['VULTR_KEY']),
            'Content-Type': 'application/json'}
class Instance:
    def __init__(self,id,label):
        self.id = id
        self.label = label


    @staticmethod
    def list_instances() -> list:
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
        response = requests.get(URL + 'instances/{}/bandwidth'.format(instance_id),headers=headers)
        bandwidth = json.loads(response.text)
        return bandwidth

# TODO: Make human readable text
    @staticmethod
    def get_instance_info(instance_id):
        response = requests.get(URL + 'instances/{}'.format(instance_id), headers=headers)
        data = json.loads(response.text)
        # formatted_data = json.dumps(data.get('instance'), indent=2 ,sort_keys=True)
        # text = 'Here is instance properties \n' + formatted_data
        # newtext = text.replace('"', ' ' , len(text))
        return data