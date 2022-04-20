import json
import requests
import vps_config as cfg

URL = 'https://api.vultr.com/v2/instances/'
headers = {'Authorization': 'Bearer {}'.format(cfg.api_keys['VULTR_KEY']),
            'Content-Type': 'application/json'}
class Instance:

    @staticmethod
    def list_instances() -> dict:
        response = requests.get(URL, headers=headers)
        data = json.loads(response.text)
        for instances in data['instances']:
            instance = {
                'id': instances['id'],
                'label':instances['label'],
                'os':instances['os'],
                'ram':instances['ram'],
                'disk':instances['disk'],
                'main_ip':instances['main_ip'],
                'vcpu_count':instances['vcpu_count'],
                'region':instances['region'],
                'server_status':instances['server_status'],
                'power_status':instances['power_status']
            }
            return instance

    @staticmethod
    def get_instance_bandwidth() -> dict:
        response = requests.get(URL + '{}/bandwidth'.format(cfg.api_keys['INSTANCE_ID']),headers)
        data = json.loads(response.text)
        for bandwidth in data['bandwidth']:
            bandwidth = {
                'server_date': {
                    'incoming_bytes':bandwidth['incoming_bytes'],
                    'outgoing_bytes':bandwidth['outgoing_bytes']
                }
            }
        print(data)
        return bandwidth
