import os
import requests
from datetime import datetime
from tqdm import tqdm
from pprint import pprint


class YaUploader:
    def __init__(self, token: str):
        self.token = token
        folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {
            'Content-Type':'application/json',
            'Accept':'application/json',
            'Authorization':f'OAuth {token}'
            }
        requests.put(f"{folder_url}?path=Загрузки/VK",headers=headers)
    

    def _get_upload_link(self, file_path: str):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {
            'Content-Type':'application/json',
            'Authorization':'OAuth {}'.format(self.token)
            }
        params = {"path":file_path, "overwrite":"true"}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    

    def upload_file_to_disk(self, file_path, file_name):
        href = self._get_upload_link(file_path=file_path).get("href","")
        response = requests.put(href, data=open(file_name,'rb'))
        return response


class VK:

   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}


   def get_user_photos(self, owner_id, num_photos = 5):
       url = 'https://api.vk.com/method/photos.getAll'
       params = {'owner_id' : owner_id,
                 'extended' :1, 
                 'count': num_photos,
                 'photo_sizes': 1}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

final_list_photos = []
photo_resolution = 'opqrsmxyzw'
photo_size ='o'
photo_url = ''

owner_id = input('Введите id пользователя vk для загрузки фото:')
ya_access_token = input('Введите токен для ЯндексДиска:')

with open(r'C:\Users\ASUS\Desktop\Maxim\vk_token.txt', 'r') as file:
    vk_access_token = file.read().strip()

uploader = YaUploader(ya_access_token)

user_id = '356407569'
vk = VK(vk_access_token, user_id)




print(f'Загружаем данные о фото пользователя {owner_id}')
for record in tqdm(vk.get_user_photos(owner_id, 200)['response']['items']):
   file_name = 'likes_'+str(record['likes']['count'])+'_'+str(record['id'])+'_'+datetime.utcfromtimestamp(record['date']).strftime('%Y_%m_%d_%H-%M-%S')+'.jpg' 
   for size in record['sizes']:
       if size['type'] in photo_resolution and photo_resolution.index(size['type'])>=photo_resolution.index(photo_size):
           photo_size = size['type']
           photo_url = size['url']
   final_list_photos.append({
    "file_name": file_name,
    "size": photo_size,
    "url": photo_url})
   photo_size = 'o'
   photo_url=''

print('\nСоздаем файл с данными о фото')
with open('photos_info.json', 'wt') as f:
        pprint(final_list_photos, stream=f)


print("Загружаем файлы на ЯндексДиск")
for record in tqdm(final_list_photos):
    r = requests.get(record['url'])
    with open('temporary.jpg', 'wb') as temporary_file:
        temporary_file.write(r.content)
    uploader.upload_file_to_disk(file_path=f"Загрузки/VK/{record['file_name']}", file_name='temporary.jpg')
    
os.remove('temporary.jpg')