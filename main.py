import vk_api
import requests
import random
from bs4 import BeautifulSoup
import hashlib


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
    # Загрузка картинки в директорию images/

    response = requests.get(image_url)

    # Имя файла - image + последние четыре символа URL (расширение файла)
    filepath = 'images/image' + image_url[-4:]

    file = open(filepath, "wb")
    file.write(response.content)
    file.close()

    return filepath


def post_vk(vk, search_query: str, user_ids: list, message: str) -> bool:
    # Авторизация Вконтакте

    # Поиск картинок и выбор одной случайной
    image_url = parse_images(search_query)
        
    # Загрузка картинки в директорию images
    try:
        filepath = download_image(image_url)
        print('Картинка успешно загружена в папку images')
    except Exception:
        print('Не удалось загрузить картинку')
        return False

    # Загрузка картинки на сервера ВКонтакте
    upload = vk_api.VkUpload(vk)
    try:
        photo = upload.photo_wall(filepath)
    except Exception:
        print('Не удалось загрузить картинку на сервера ВКонтакте')
        return False

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
        if not message:
            message = 'Sent with python script'

        post_vk(vk, search_text, user_ids, message)

        print("Рассылка закончена")
        print("=" * 40 + '\n')
