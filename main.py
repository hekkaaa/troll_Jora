import vk_api
import hashlib

search_text = input('Введите текст для поиска открытки.\n\
Например: православные открытки с надписями\nИскать: ')

YANDEX_SEARCH = f'https://yandex.ru/images/search?from=tabbar&nomisspell=1&text={search_text}&source=related-0'

print("Введите ваш логин VK")
LOGIN = input()
print("Введите пароль")
INPUTPASS = input()
print("принимаются id только в цифрах и без пробелов!!!")
print("Введите через запятую id нужных пользователей: ")
ID_USER = input()
ID_USER = ID_USER.split(',')

# # хеширование пароля
hash_object = hashlib.sha256(INPUTPASS.encode())
hex_dig = hash_object.hexdigest()

####
def parser_images(YANDEX_SEARCH):
    response = requests.get(YANDEX_SEARCH)
    print(response.status_code)
    soup = BeautifulSoup(response.content, "html.parser")
    agg = soup.find_all('a', 'serp-item__link')
    if (agg == []):
        print('Error - вероятно яндекс ссылка опять дико тупит. Попробуй еще раз')
        return False
    else:
        random_number = random.randint(0, len(agg) - 1)

        # Вторая итерация получения прямой картинки
        # response = requests.get('https://yandex.ru'+agg[random_number]['href'])
        result_2 = 'https://yandex.ru' + agg[random_number]['href']
        return result_2

        # Эта часть обрезана по причине того что VK.api не ждет ссылки "//im0-tub-ru.yandex.net/i?id=b5120b88709074ee9bbc08c4b34a16b5&n=13"
        # даже если дополнить их. В ручную если кидать на сайте то все ок. ХЗ в чем проблема.

        # soup = BeautifulSoup(response.content, "html.parser")
        # agg = soup.find_all('img')
        # random_number = random.randint(0,len(agg)-1)
        # pre_result = agg[random_number]['data-thumb']
        # result = 'https:'+ pre_result
        # return result

# ВК авторизация и пост на стену.
def VK_POST(LOGIN, PASS, YANDEX_SEARCH,ID_USER):
    vk_session = vk_api.VkApi(LOGIN, PASS)
    vk_session.auth()

    vk = vk_session.get_api()

    url_images = parser_images(YANDEX_SEARCH)
    if (url_images == False):
        print("Не взлетело")
        return False
    else:
        # Отправка картинки на стену пользователю.
        for ID_USER in ID_USER:
            try:
                vk.wall.post(message="Post sent by Python script", attachments=url_images, owner_id=ID_USER)
            except vk_api.exceptions.ApiError:
                print(f"Error! Ошибка ID '{ID_USER}'. Не верно указан id, либо стена закрыта для записи")
            except:
                print("ERROR!")
    return True

VK_POST(LOGIN,hex_dig,YANDEX_SEARCH,ID_USER)