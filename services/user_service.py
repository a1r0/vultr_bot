import json
import requests
import vps_config as cfg

"""TODO : Rewrite as instance plugin"""

class User:

    @staticmethod
    def load_user_profiles() -> dict:
        url = 'https://api.vultr.com/v2/users'
        headers = {'Authorization': 'Bearer {}'.format(cfg.api_keys['VULTR_KEY']),
                    'Content-Type': 'application/json'}

        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        return data['users']

    @staticmethod
    def get_user_list() -> list:
        userlist = User.load_user_profiles()
        users = []
        for user in userlist:
            user = {
                'name': user['name'],
                'id': user['id'],
                'mail': user['email']
            }
            users.append(user)
        return users

    @staticmethod
    def get_full_profile(id) -> str:
        url = f'https://api.vultr.com/v2/users{id}'
        headers = {'Authorization': 'Bearer {}'.format(cfg.api_keys['VULTR_KEY']),
                    'Content-Type': 'application/json'}
        response = requests.get(url , headers=headers)
        data = json.loads(response.text)
        user = []
        for i in data['user']:
            i = {
                "id": i['id'],
                "name": i['name'],
                "email": i['email'],
                "api_enabled": i['api_enabled'],
            }
        user.append(i)
        return(user)
        

user = User()
