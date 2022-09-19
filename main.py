import os
import random
import requests
import shutil

from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse


def get_upload_url(url, params):
    metod = 'photos.getWallUploadServer'
    vk_url = f'{url}/{metod}'
    vk_response = requests.get(vk_url, params=params)
    vk_response_json = vk_response.json()
    try:
        upload_url = vk_response_json['response']['upload_url']
    except KeyError:
        upload_url = None
        print('Не удалось получить адрес для загрузки.')
        return
    return upload_url


def upload_photo(url, upload_url, params, comics_to_upload):
    with open(image_dir.joinpath(file_name), 'rb') as file:
        url = upload_url
        files = {'photo': file}
        response = requests.post(url, files=files)
        response.raise_for_status()
    response_json = response.json()
    return response_json['server'], response_json['photo'], response_json['hash']


def save_photo(url, params):
    metod = 'photos.saveWallPhoto'
    vk_url = f'{url}/{metod}'
    response = requests.post(vk_url, params=params)
    response.raise_for_status()
    response_json = response.json()
    media_id = response.json()['response'][0]['id']
    owner_id = response_json['response'][0]['owner_id']
    return media_id, owner_id


def post_photo(url, params):
    metod = 'wall.post'
    vk_url = f'{url}/{metod}'
    response = requests.post(vk_url, params=params)
    response.raise_for_status()
    return response


def get_last_comics_num(url):
    last_num = 1
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return
    response_json = response.json()
    last_num = response_json['num']
    return last_num


IMAGE_FOLDER_NAME = 'Comics_Images'


if __name__ == '__main__':
    load_dotenv()
    url = 'https://xkcd.com'
    last_comics_url = 'https://xkcd.com/info.0.json'
    last_comics_num = get_last_comics_num(last_comics_url)
    comics_number = str(random.randint(1, last_comics_num))
    comics_path = 'info.0.json'
    comics_url = f'{url}/{comics_number}/{comics_path}'
    try:
        response = requests.get(comics_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        response = requests.get(last_comics_url)

    comics_json = response.json()

    current_dir = Path.cwd()
    image_dir = current_dir.joinpath(IMAGE_FOLDER_NAME)
    Path.mkdir(image_dir, exist_ok=True)

    file_name = Path(urlparse(comics_json['img']).path).name

    with open(image_dir.joinpath(file_name), 'wb') as file:
        img_responce = requests.get(comics_json['img'])
        file.write(img_responce.content)

    comment = comics_json['alt']

    vk_url = 'https://api.vk.com/method/'

    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    vk_user_id = os.getenv('VK_USER_ID')

    params = {'group_id': vk_group_id,
              'access_token': vk_token,
              'v': 5.131,
              }

    upload_url = get_upload_url(vk_url, params)

    server, photo, vk_hash = upload_photo(vk_url,
                                          upload_url,
                                          params,
                                          image_dir.joinpath(file_name)
                                          )

    params = {'group_id': vk_group_id,
              'access_token': vk_token,
              'v': 5.131,
              'server': server,
              'photo': photo,
              'hash': vk_hash
              }

    media_id, owner_id = save_photo(vk_url, params)

    params = {'owner_id': f'-{vk_group_id}',
              'access_token': vk_token,
              'v': 5.131,
              'from_group': 0,
              'message': comics_json['alt'],
              'attachments': f'photo{owner_id}_{media_id}'
              }

    post_photo(vk_url, params)
    shutil.rmtree(image_dir)
