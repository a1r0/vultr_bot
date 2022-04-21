import json
import requests
import vps_config as cfg
class User:

    @staticmethod
    def load_user_profile() -> dict:
        url = 'https://api.vultr.com/v2/users'
        headers = {'Authorization': 'Bearer {}'.format(cfg.api_keys['VULTR_KEY']),
                    'Content-Type': 'application/json'}

        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        for users in data['users']:
            userprofile = {
                'name':users['name'],
                'id': users['id'],
                'email':users['email']
            }
            return userprofile

    @staticmethod
    def get_user_name() -> str:
        userprofile = User.load_user_profile()
        return userprofile['name']

    @staticmethod
    def get_user_userid() -> str:
        userprofile = User.load_user_profile()
        return userprofile['id']

    @staticmethod
    def get_user_email() -> str:
        userprofile = User.load_user_profile()
        return userprofile['email']

user = User()
