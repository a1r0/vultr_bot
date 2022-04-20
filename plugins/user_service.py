import json
import requests
from vps_config import vultr_key

class User:
    pass
        
    def load_user_profile() -> dict: 
        url = 'https://api.vultr.com/v2/users'
        headers = {'Authorization': 'Bearer {}'.format(vultr_key),
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

    def get_user_name(self) -> str:        
        userprofile = User.load_user_profile()
        return userprofile['name']

    def get_user_userid(self) -> str:
        userprofile = User.load_user_profile()
        return userprofile['id']
    
    def get_user_email(self) -> str:
        userprofile = User.load_user_profile()
        return userprofile['email']
        
user = User()

