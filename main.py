import vk_api
import requests
import random
from bs4 import BeautifulSoup
import hashlib


def parse_images(search_text: str) -> str or None:
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

    if response.status_code == 200:
        print('Картинки получены')
    else:
        print(f'Не могу получить картинки по запросу {search_text}')
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    agg = soup.find_all('a', 'serp-item__link')
    if not agg:
        print('Ошибка - вероятно яндекс ссылка опять дико тупит. Попробуй еще раз')
        return None
    else:
        # Выбор случайной картинки из полученного ответа
        random_number = random.randint(0, len(agg) - 1)
        image_link = requests.utils.unquote(agg[random_number]['href'])

        # Получение индексов начала и конца ссылки на источник картинки
        start = image_link.find('img_url=') + len('img_url=')
        end = image_link[start:].find('&') + start

        # Обрезка ссылки для получения ссылки на источник
        image_link = image_link[start:end]

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


def post_vk(login: str, password: str, search_query: str, user_ids: list, message: str) -> bool:
    # Авторизация Вконтакте
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()

    vk = vk_session.get_api()

    # Поиск картинок и выбор одной случайной
    image_url = parse_images(search_query)

    if not image_url:
        print("Не взлетело")
        return False
    else:
        # Отправка картинки на стену пользователю.

        # Загрузка картинки в директорию images
        try:
            filepath = download_image(image_url)
            print('Картинка успешно загружена в папку images')
        except Exception:
            print('Не удалось загрузить картинку')
            return False

        # Загрузка картинки на сервера ВКонтакте
        upload = vk_api.VkUpload(vk)

        # Здесь просходит ошибка [100]
        # vk_api.exceptions.ApiError: [100] One of the parameters specified was missing or invalid: photos_list is invalid
        # ВК не нравится картинка.
        try:
            photo = upload.photo_wall(filepath)
        except vk_api.exceptions.ApiError as ex:
            print("Ошибка загрузки картинки. Попробуйте еще раз")
            print(ex)
            return False
        except:
            print("Неизвестная ошибка :(")
            return True

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


if __name__ == "__main__":

    login = input("Введите ваш логин VK: ")
    password = input("Введите ваш пароль: ")

    ## хеширование пароля
    hash_object = hashlib.sha256(password.encode())
    password = hash_object.hexdigest()

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

        post_vk(login, password, search_text, user_ids, message)

        print("Рассылка закончена")
        print("=" * 40 + '\n')
