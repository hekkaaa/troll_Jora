import vk_api
import requests
import random
from bs4 import BeautifulSoup

def parse_images(search_text: str) -> str or None:

    # Адрес запроса картинок
    query = 'https://yandex.ru/images/search'

    # Параметры запроса
    params = {
        "from" :        "tabbar", 
        "nomisspell":   1, 
        "text":         search_text, 
        "source" :      "related-0"}

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


def post_vk(login: str, password: str, search_query: str, user_ids: list, message: str) -> bool:

    # Авторизация Вконтакте
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()

    vk = vk_session.get_api()

    url_images = parse_images(search_query)
    if not url_images:
        print("Не взлетело")
        return False
    else:
        # Отправка картинки на стену пользователю.
        for user_id in user_ids:
            try:
                vk.wall.post(message=message, 
                attachments=url_images, owner_id=user_id)
                print('Картинка отправлена на стену пользователя!')
            except vk_api.exceptions.ApiError as ex:
                print(f"\nError! Ошибка ID '{user_id}':")
                print(ex)
            except Exception:
                print("Неизвестная ошибка :(")
    return True


if __name__ == "__main__":

    while True:
        print('Введите текст для поиска открытки.')
        print('Например: православные открытки с надписями')
        search_text = input('Искать: ')

        login = input("Введите ваш логин VK: ")
        password = input("Введите ваш пароль: ")

        # Получение списка ID пользователей, разделенных запятыми
        user_ids = input("Введите через запятую id нужных пользователей: ").split(',')
        # Удаление пустых значений и пробелов
        user_ids = [user_id.strip() for user_id in user_ids if user_id]

        message = input('Введите подпись для картинки (необязательно): ')
        if not message:
            message = 'Sent with python script'

        post_vk(login, password, search_text, user_ids, message)
