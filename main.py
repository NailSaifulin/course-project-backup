import json
from datetime import datetime
from tqdm import tqdm
import requests


with open('token_vk.txt', 'r') as file_object:
    token_vk = file_object.read().strip()


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token_vk, version):
        self.params = {
            'access_token': token_vk,
            'v': version
        }

    def get_photos(self, vk_id, count_photo):
        get_photos_url = self.url + 'photos.get'
        get_photos_params = {
            'owner_id': vk_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'count': count_photo
        }
        req = requests.get(get_photos_url, params={**self.params, **get_photos_params}).json()
        return req


class YaUploader:
    def __init__(self, token_ya: str):
        self.token_ya = token_ya

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def create_folder(self, path):
        headers = self.get_headers()
        folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
        requests.put(f'{folder_url}?path={path}', headers=headers)

    def upload(self, disk_file_path: str, url_photo):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "url": url_photo}
        response = requests.post(upload_url, headers=headers, params=params)
        # if response.status_code == 202:
        #     print("Success")


def photo_post():
    json_name_size = []  # список для формирования json файла
    name_photo = []  # cписок с названиями фото, для проверки на повторяемость
    vk_client = VkUser(token_vk, '5.131')
    json_vk = vk_client.get_photos(input("Введите id пользователя vk "), input("Введите количество загружаемых фото "))
    uploader = YaUploader(input("Введите токен с полигона Яндекс диска "))
    uploader.create_folder('netology')
    for items_vk in tqdm(json_vk['response']['items'], desc="Photos", unit=" photo", ncols=100):
        if len(name_photo) and str(items_vk['likes']['count']) + '.jpg' in name_photo:
            FORMAT = '%d-%m-%Y'
            uploader.upload("netology/" + str(items_vk['likes']['count']) + '_' +
                            datetime.now().strftime(FORMAT) + '.jpg',
                            items_vk['sizes'][-1]['url'])
            json_name_size.append({'file_name': str(items_vk['likes']['count']) + '_' +
                                                datetime.now().strftime(FORMAT) + '.jpg',
                                   'size': items_vk['sizes'][-1]['type']})
            name_photo.append(str(items_vk['likes']['count']) + '_' +
                              datetime.now().strftime(FORMAT) + '.jpg')
        else:
            uploader.upload("netology/" + str(items_vk['likes']['count']) + '.jpg', items_vk['sizes'][-1]['url'])
            json_name_size.append({'file_name': str(items_vk['likes']['count']) + '.jpg',
                                   'size': items_vk['sizes'][-1]['type']})
            name_photo.append(str(items_vk['likes']['count']) + '.jpg')

    with open("name_size_photo.json", "w") as f:
        json.dump(json_name_size, f)


photo_post()

