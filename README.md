# Публикация комиксов в сообщество VK

Скрипт для публикации комиксов с ресурса https://xkcd.com/ на стену сообщества ВКонтакте https://vk.com.

Для работы понадобится PYthon3 и библиотеки из файла requirements.txt.

Архив с проектом нужно скачать к себе на компьютер и распаковать в любую удобную директорию.

## Подготовка переменных окружения

Перед запуском проекта нужно подготовить .env файл с переменными окружения, шаблон файла сохранен в папке проекта и содержит следующие переменные:

```
VK_CLIENT_ID=

VK_ACCESS_TOKEN=

VK_USER_ID=

VK_GROUP_ID = 
```

Также нужно иметь аккаунт [ВКонтакте](https://vk.com) и сообщество, где будут публиковаться комиксы о Python.

После того, как будет создан аккаунт, на [странице разработчиков](https://vk.com/editapp?act=create) нужно создать standalone-приложение:
![](https://github.com/atskayasatana/Images/blob/fd1c5aed52faa501d446540caa5a4c025a330338/new_app_vk.png)

Переходим в настройки и копируем ID приложения в .env файл, переменная VK_CLIENT_ID.

![](https://github.com/atskayasatana/Images/blob/fd1c5aed52faa501d446540caa5a4c025a330338/id_vk_app.png)

Получим токен для пользователя по инструкции [здесь](https://dev.vk.com/api/access-token/implicit-flow-user):
1. Вводим в адресной строке:
```
https://oauth.vk.com/authorize?client_id=<наш VK_CLIENT_ID>&display=page&scope=friends,photos,groups&response_type=token&v=5.131&state=123456
```
2. В появившемся окне жмём "Разрешить"

![](https://github.com/atskayasatana/Images/blob/fd1c5aed52faa501d446540caa5a4c025a330338/vk_app_token.png)

3. Копируем из адресной строки появившегося окна в .env токен(переменная VK_ACCESS_TOKEN) и user_id(переменная VK_USER_ID)

![](https://github.com/atskayasatana/Images/blob/fd1c5aed52faa501d446540caa5a4c025a330338/vk_token_final.png)

Также нам понадобится id созданного сообщества, узнать его можно [здесь](https://regvk.com/id/) или на своей странице зайти в Сообщества->Настройки
и в поле Адрес скопировать цифры после public.

![](https://github.com/atskayasatana/Images/blob/fd1c5aed52faa501d446540caa5a4c025a330338/vk_group_id.png)

## Запуск скрипта

Запускаем командную строку и переходим в директорию проекта.

Устанавливаем зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
Запускаем проект:
```
python main.py
```
Если не было никаких сообщений об ошибке, то на стене сообщества появится случайный комикс и комментарий автора к нему.

![](https://github.com/atskayasatana/Images/blob/fd1c5aed52faa501d446540caa5a4c025a330338/vk_final.png)

## Основные функции

Картинка на стене во Вконтакте публикуется в несколько этапов:

Получение адреса для загрузки фото

Загрузка фото на сервер

Сохранение фото в альбоме группы

Публикация записи в группе

В качестве url во всех функциях используется https://api.vk.com/method/

### def get_upload_url(url,params)

Получает адрес для загрузки фото, в params передается словарь с id сообщества, токеном и версией приложения.
Возвращает адрес для загрузки картинки

### def upload_photo(url, upload_url, params, comics_to_upload)

Загружает фото на сервер, в качестве параметров params передается словарь с id сообщества, токеном и версией приложения, в upload_url - результат работы функции
get_upload_url.

Возвращает 3 параметра: server, photo и hash, которые понадобятся для сохранения картинки.

### save_photo(url, params)

Сохраняет картинку в альбоме группы, в params передаются server, photo, hash полученные из функции upload_photo, а также id сообщества, токен и версия приложения.

Возвращает media_id и owner_id, нужные для публикации картинки на стену.

### post_photo(url, params)

Публикует картинку в сообщество, в params передаются параметры авторизации, а также media_id и owner_id полученные после работы функции save_photo.

Возвращает id опубликованного поста.

### get_last_comics_num(url)

Возвращает номер последнего комикса, который публиковался на https://xkcd.com/

### def get_random_comic()

Находит случайный комикс. Возвращает ссылку на изображение с комиксом и текст комментария к нему.
