import vk_api
import requests
import random
from bs4 import BeautifulSoup


def parse_images(search_text):

    # Адрес запроса картинок
    query = 'https://yandex.ru/images/search'

    # Параметры запроса
    params = {
        "from" :        "tabbar", 
        "nomisspell":   1, 
        "text":         search_text, 
        "source" :      "related-0"}

    # Передача GET запроса на сервер
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
        random_number = random.randint(0, len(agg) - 1)

        # Вторая итерация получения прямой картинки
        result = 'https://yandex.ru' + agg[random_number]['href']
        return result


# ВК авторизация и пост на стену.
def post_vk(login, password, search_query, user_ids):
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
                vk.wall.post(message="Post sent by Python script", 
                attachments=url_images, owner_id=user_id)
            except vk_api.exceptions.ApiError:
                print(f"Ошибка ID '{user_id}'. Неверно указан ID, либо стена закрыта для записи")
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

        post_vk(login, password, search_text, user_ids)