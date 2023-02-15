import requests
import time
from pprint import pprint

class VK:

   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

   def users_info(self):
       url = 'https://api.vk.com/method/users.get'
       params = {'user_ids': self.id,
                 'fields' :'education, sex'}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

with open('vk_token.txt', 'r') as file:
    access_token = file.read().strip()

user_id = '356407569'
vk = VK(access_token, user_id)
pprint(vk.users_info())

