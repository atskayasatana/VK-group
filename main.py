import os
import random
import requests
import shutil

from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse

IMAGE_FOLDER_NAME = 'Comics_Images'


def get_upload_url(vk_group_id, vk_token, ver):
    url = 'https://api.vk.com/method/'
    metod = 'photos.getWallUploadServer'
    vk_url = f'{url}/{metod}'
    params = {'group_id': vk_group_id,
              'access_token': vk_token,
              'v': ver
              }
    vk_response = requests.get(vk_url, params=params)
    upload_url = vk_response.json()['response']['upload_url']
    return upload_url


def upload_photo(upload_url,
                 comic_dir,
                 comic_file,
                 vk_group_id,
                 vk_token,
                 ver
                 ):
    file = open(comic_dir.joinpath(comic_file), 'rb')
    files = {'photo': file}
    response = requests.post(upload_url, files=files)
    response.raise_for_status()
    file.close()
    upload_data = response.json()
    return upload_data['server'], upload_data['photo'], upload_data['hash']


def save_photo(vk_group_id, vk_token, ver, server, photo, vk_hash):
    url = 'https://api.vk.com/method/'
    metod = 'photos.saveWallPhoto'
    vk_url = f'{url}/{metod}'
    params = {'group_id': vk_group_id,
              'access_token': vk_token,
              'v': ver,
              'server': server,
              'photo': photo,
              'hash': vk_hash
              }
    response = requests.post(vk_url, params=params)
    response.raise_for_status()
    save_photo_metadata = response.json()
    media_id = save_photo_metadata['response'][0]['id']
    owner_id = save_photo_metadata['response'][0]['owner_id']
    return media_id, owner_id


def post_photo(vk_group_id, vk_token, ver, text, owner_id, media_id):
    url = 'https://api.vk.com/method/'
    metod = 'wall.post'
    vk_url = f'{url}/{metod}'
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


def get_last_comic_num(url):
    last_num = 1
    response = requests.get(url)
    response.raise_for_status()
    last_num = response.json()['num']
    return last_num


def get_random_comic():
    url = 'https://xkcd.com'
    last_comics_url = 'https://xkcd.com/info.0.json'
    try:
        last_comics_num = get_last_comic_num(last_comics_url)
    except requests.exceptions.HTTPError:
        last_comics_num = 1
    comics_number = str(random.randint(1, last_comics_num))
    comics_path = 'info.0.json'
    comics_url = f'{url}/{comics_number}/{comics_path}'
    try:
        response = requests.get(comics_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        response = requests.get(last_comics_url)
    comics_metadata = response.json()
    image = comics_metadata['img']
    comment = comics_metadata['alt']
    return image, comment


def main():
    load_dotenv()

    vk_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')
    ver = 5.131

    image, comment = get_random_comic()

    current_dir = Path.cwd()
    image_dir = current_dir.joinpath(IMAGE_FOLDER_NAME)
    Path.mkdir(image_dir, exist_ok=True)

    file_name = Path(urlparse(image).path).name

    try:
        with open(image_dir.joinpath(file_name), 'wb') as file:
            img_responce = requests.get(image)
            file.write(img_responce.content)
            
        upload_url = get_upload_url(vk_group_id, vk_token, ver)
        


        server, photo, vk_hash = upload_photo(upload_url,
                                              image_dir,
                                              file_name,
                                              vk_group_id,
                                              vk_token,
                                              ver
                                              )

        media_id, owner_id = save_photo(vk_group_id,
                                        vk_token,
                                        ver,
                                        server,
                                        photo,
                                        vk_hash)
        post_photo(vk_group_id, vk_token, ver, comment, owner_id, media_id)
        
    except ValueError:
        print('Не удалось загрузить файл')

    except KeyError:
        print('Не удалось получить параметры загрузки')

    finally:
        shutil.rmtree(image_dir)


if __name__ == '__main__':
    main()
