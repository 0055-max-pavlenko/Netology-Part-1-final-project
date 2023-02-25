import os
import requests
import time
from datetime import datetime, date
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
        requests.put(f"{folder_url}?path=VK_backup_{date.today()}",headers=headers)
    

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


   def get_user_photos(self, owner_id, num_photos = 5, offset = 0):
       url = 'https://api.vk.com/method/photos.getAll'
       params = {'owner_id' : owner_id,
                 'extended' :1, 
                 'count': num_photos,
                 'photo_sizes': 1,
                 'offset': offset}
       response = requests.get(url, params={**self.params, **params})
       return response.json()

def Upload_photos_VK_YandexDrive (owner_backup_id, ya_access_token, vk_access_id, vk_access_token):

    final_list_photos = []
    photo_resolution = 'opqrsmxyzw'
    photo_size ='o'
    photo_url = ''
    
    
    vk = VK(vk_access_token, vk_access_id)
    uploader = YaUploader(ya_access_token)
    total_number_photos = vk.get_user_photos(owner_backup_id)['response']['count']
    counter = 0


    time.sleep(0.5)

    print(f'Загружаем данные о фото пользователя {owner_backup_id}')
    while counter<=total_number_photos:
        for record in vk.get_user_photos(owner_backup_id, 200, counter)['response']['items']:
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
        counter += 200
        time.sleep(0.5)
    print('\nСоздаем файл с данными о фото')
    with open('photos_info.json', 'wt') as f:
        pprint(final_list_photos, stream=f)


    print("Загружаем файлы на ЯндексДиск")
    for record in tqdm(final_list_photos):
        r = requests.get(record['url'])
        with open('temporary.jpg', 'wb') as temporary_file:
            temporary_file.write(r.content)
        uploader.upload_file_to_disk(file_path=f"VK_backup_{date.today()}/{record['file_name']}", file_name='temporary.jpg')
    
    os.remove('temporary.jpg')



owner_backup_id = input('Введите id пользователя vk для загрузки фото:')
ya_access_token = input('Введите токен для ЯндексДиска:')
print()
vk_access_id = input('Введите id пользователя, владельца приложения для сохранения фото:')
vk_access_token = input('Введите токен для vk приложения для сохранения фото:')

Upload_photos_VK_YandexDrive (owner_backup_id, ya_access_token, vk_access_id, vk_access_token)




