import json
import requests
from config import vultr_key

class Instance:
    pass

def list_instances() -> dict:
    url = 'https://api.vultr.com/v2/instances'
    headers = {'Authorization': 'Bearer {}'.format(vultr_key),
                'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)
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
print(list_instances())