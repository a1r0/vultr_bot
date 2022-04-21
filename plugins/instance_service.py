import json
import requests
import vps_config as cfg

URL = 'https://api.vultr.com/v2/instances'
headers = {'Authorization': 'Bearer {}'.format(cfg.api_keys['VULTR_KEY']),
            'Content-Type': 'application/json'}
class Instance:

    @staticmethod
    def list_instances() -> list:
        response = requests.get(URL, headers=headers)
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
    def get_instance_bandwidth() -> dict:
        response = requests.get(URL + '{}/bandwidth'.format(cfg.api_keys['INSTANCE_ID']),headers=headers)
        data = json.loads(response.text)
        for result in data['bandwidth']:
            result = {
                'server_date': {
                    'incoming_bytes':result['incoming_bytes'],
                    'outgoing_bytes':result['outgoing_bytes']
                }
            }
        print(data)
        return result

# TODO: Instance info
    @staticmethod
    def get_instance_info(instance_id) -> dict:
        response = requests.get(URL + '/{}'.format(instance_id), headers=headers)
        data = json.loads(response.text)
        return data
