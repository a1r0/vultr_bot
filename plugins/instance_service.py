import json
import requests
from vps_config import vultr_key,instance_id
class Instance:
    pass
URL = 'https://api.vultr.com/v2/instances/'
headers = {'Authorization': 'Bearer {}'.format(vultr_key),
            'Content-Type': 'application/json'}

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

def get_instance_bandwidth() -> dict:
    response = requests.get(URL + '{}/bandwidth'.format(instance_id),headers)
    data = json.loads(response.text)
    for bandwidth in data['bandwidth']:
        bandwidth = {
            'server_date': {
                'incoming_bytes':bandwidth['incoming_bytes'],
                'outgoing_bytes':bandwidth['outgoing_bytes']
            }
        }
    return bandwidth
print(get_instance_bandwidth())