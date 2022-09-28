import os
import random
import requests
import shutil

from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse

IMAGE_FOLDER_NAME = 'Comics_Images'


def get_upload_url(vk_group_id, vk_token, ver):
    vk_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {'group_id': vk_group_id,
              'access_token': vk_token,
              'v': ver
              }
    vk_response = requests.get(vk_url, params=params)
    vk_response.raise_for_status()
    upload_url = vk_response.json()['response']['upload_url']
    return upload_url


def upload_photo(
        upload_url, comic_dir, comic_file,
        vk_group_id, vk_token, ver):

    params = {'group_id': vk_group_id,
              'access_token': vk_token,
              'v': ver
              }
    with open(comic_dir.joinpath(comic_file), 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, params=params, files=files)
    response.raise_for_status()
    photo_metadata = response.json()
    return photo_metadata['server'], photo_metadata['photo'], photo_metadata['hash']


def save_photo(
        vk_group_id, vk_token, ver,
        server, photo, vk_hash):
    vk_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {'group_id': vk_group_id,
              'access_token': vk_token,
              'v': ver,
              'server': server,
              'photo': photo,
              'hash': vk_hash
              }
    response = requests.post(vk_url, params=params)
    response.raise_for_status()
    photo_metadata = response.json()
    media_id = photo_metadata['response'][0]['id']
    owner_id = photo_metadata['response'][0]['owner_id']
    return media_id, owner_id


def post_photo(
        vk_group_id, vk_token, ver,
        text, owner_id, media_id):
    vk_url = 'https://api.vk.com/method/wall.post'
    params = {'owner_id': f'-{vk_group_id}',
              'access_token': vk_token,
              'v': ver,
              'from_group': 0,
              'message': text,
              'attachments': f'photo{owner_id}_{media_id}'
              }
    response = requests.post(vk_url, params=params)
    response.raise_for_status()

    return response


def get_random_comic():

    url = 'https://xkcd.com'
    last_comic_url = 'https://xkcd.com/info.0.json'

    last_comic_responce = requests.get(last_comic_url)
    last_num = last_comic_responce.json()['num']

    comics_number = random.randint(1, last_num)
    comics_url = f'{url}/{comics_number}/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()
    comics_metadata = response.json()
    image = comics_metadata['img']
    comment = comics_metadata['alt']
    return image, comment


def main():
    load_dotenv()

    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    ver = 5.131

    current_dir = Path.cwd()
    image_dir = current_dir.joinpath(IMAGE_FOLDER_NAME)
    Path.mkdir(image_dir, exist_ok=True)

    try:
        image, comment = get_random_comic()
        print(comment)
        file_name = Path(urlparse(image).path).name
        print(file_name)

        with open(image_dir.joinpath(file_name), 'wb') as file:
            img_responce = requests.get(image)
            file.write(img_responce.content)

        upload_url = get_upload_url(vk_group_id, vk_token, ver)
        print(upload_url)

        server, photo, vk_hash = upload_photo(upload_url, image_dir, file_name,
                                              vk_group_id, vk_token, ver)

        media_id, owner_id = save_photo(vk_group_id, vk_token, ver,
                                        server, photo, vk_hash)

        post_photo(vk_group_id, vk_token, ver, comment, owner_id, media_id)

    except requests.exceptions.HTTPError as http_error:
        print('Ошибка в запросе')
        print(http_error.status_code)
        print(http_error.response.text)

    except KeyError as key_error:
        print('Не удалось получить параметры загрузки')
        print(key_error)
        
    finally:
        shutil.rmtree(image_dir)


if __name__ == '__main__':
    main()
