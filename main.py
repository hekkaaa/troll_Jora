import vk_api
import requests
import random
from bs4 import BeautifulSoup
import os


def handle_image_link(image_link: str) -> str:
    # Выделение ссылки на источник картинки из Яндекс-ссылки

    # Получение индексов начала и конца ссылки на источник картинки
    start = image_link.find('img_url=') + len('img_url=')
    end = image_link[start:].find('&') + start

    # Обрезка ссылки для получения ссылки на источник
    image_link = image_link[start:end]

    # Дополнительная проверка
    if image_link.find('?') != -1:
        end = image_link.find('?')
        image_link = image_link[:end]

    return image_link


def parse_images(search_text: str) -> str or None:
    # Получение картинок по запросу и возврат ссылки на одну случайную

    # Адрес запроса картинок
    query = 'https://yandex.ru/images/search'

    # Параметры запроса
    params = {
        "from": "tabbar",
        "nomisspell": 1,
        "text": search_text,
        "source": "related-0"}

    # Отправка GET запроса на сервер
    response = requests.get(query, params=params)

    if 'captcha' in response.text:
        print('Ошибка - Яндекс запрашивает капчу. Попробуйте позже')
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    agg = soup.find_all('a', 'serp-item__link')
    if not agg:
        print('Ошибка - вероятно яндекс ссылка опять дико тупит. Попробуй еще раз')
        return None

    # Выбор случайной картинки из полученного ответа
    image_link = ''
    while image_link[-4:] not in ['.jpg', '.png', '.bmp', '.gif']:
        random_number = random.randint(0, len(agg) - 1)
        image_link = requests.utils.unquote(agg[random_number]['href'])
        image_link = handle_image_link(image_link)

    return image_link


def download_image(image_url: str) -> str:
    # Загрузка картинки в текущую директорию

    response = requests.get(image_url)

    # Имя файла - image + последние четыре символа URL (расширение файла)
    filepath = 'image' + image_url[-4:]

    file = open(filepath, "wb")
    file.write(response.content)
    file.close()

    return filepath


def post_vk(vk, search_query: str, user_ids: list, message: str) -> bool:
    # Авторизация Вконтакте

    # Загрузка картинки
    count = 0 # Значение для ошибки загрузки картинки.
    while True:
        try:
            # Получение ссылки на случайную картинку
            image_url = parse_images(search_query)

            # Загрузка картинки в текущую директорию
            filepath = download_image(image_url)

            # Загрузка картинки на сервера ВК
            photo = vk_api.VkUpload(vk).photo_wall(filepath)

            # Удаление загруженной картинки из текущей директории
            os.remove(filepath)

            # Выход из цикла
            print('Картинка успешно загружена')
            break

        except Exception:
            # Если возникла ошибка - повторить

            if count == 5:
                # Если уже 5 попыток то значит баг.
                print("Вероятнее всего цикл завис. Перезапустите скрипт.")
                break
            else:
                count+1
                continue

    # Получение данных картинки из ответа VK API
    owner_id = photo[0]['owner_id']
    photo_id = photo[0]['id']
    access_key = photo[0]['access_key']

    # Создание ВК-ссылки на картинку
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'

    # Постинг картинки каждому юзеру из user_ids
    for user_id in user_ids:
        try:
            vk.wall.post(message=message,
                         attachments=attachment, owner_id=user_id)
            print(f'Картинка отправлена на стену пользователя {user_id}!')
        except vk_api.exceptions.ApiError as ex:
            print(f"\nError! Ошибка ID '{user_id}':")
            print(ex)
        except Exception:
            print("Неизвестная ошибка :(")

    return True


def auth_vk(login: str, password: str) -> vk_api.vk_api.VkApiMethod:
    # Авторизация Вконтакте

    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()

    return vk_session.get_api()


if __name__ == "__main__":

    # Зачистка файла авторизации json от прошлого запуска скрипта.
    if os.path.isfile('vk_config.v2.json'):
        os.remove('vk_config.v2.json')

    while True:
        login = input("Введите ваш логин VK: ")
        password = input("Введите ваш пароль: ")

        try:
            vk = auth_vk(login, password)
            print('Авторизация ВКонтакте прошла успешно!')
            break
        except vk_api.exceptions.BadPassword:
            print('Неверный пароль. Попробуйте еще раз.')
        except Exception as ex:
            print('Не удалось пройти авторизацию. Возникла ошибка:', ex)

    while True:
        print('Введите текст для поиска открытки. Например: "православные открытки с надписями"\n')
        search_text = input('Искать: ')

        # Получение списка ID пользователей, разделенных запятыми
        user_ids = input("Введите через запятую id нужных пользователей: ").split(',')
        # Удаление пустых значений и пробелов
        user_ids = [user_id.strip() for user_id in user_ids if user_id]

        message = input('Введите подпись для картинки (необязательно): ')
        try:
            count = int(input('Введите количество постов (по умолчанию: 1): '))
        except ValueError:
            count = 1
            print('Не понял ответа. Установлено значение по умолчанию')

        for i in range(count):
            post_vk(vk, search_text, user_ids, message)
            print(f'Опубликовано постов: {i + 1}/{count}')

        print("Рассылка закончена")
        print("=" * 40 + '\n')
