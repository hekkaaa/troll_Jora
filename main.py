import vk_api
import hashlib

print("Введите ваш логин VK")
LOGIN = input()
print("Введите пароль")
INPUTPASS = input()

#Ссылка на картинки
YANDEX_SEARCH ='https://yandex.ru/images/search?from=tabbar&text=%D0%BF%D1%80%D0%B0%D0%B2%D0%BE%D1%81%D0%BB%D0%B0%D0%B2%D0%BD%D1%8B%D0%B5%20%D0%BE%D1%82%D0%BA%D1%80%D1%8B%D1%82%D0%BA%D0%B8'


# хеширование пароля
hash_object = hashlib.sha256(INPUTPASS.encode())
hex_dig = hash_object.hexdigest()

####

def parser_images(YANDEX_SEARCH):
    response = requests.get(YANDEX_SEARCH)
    print(response.status_code)
    soup = BeautifulSoup(response.content, "html.parser")
    agg = soup.find_all('a','serp-item__link')
    print(agg)
    if (agg == []):
        print('Error - вероятно яндекс ссылка опять дико тупит. Попробуй еще раз')
        return False
    else:
        random_number = random.randint(0,len(agg)-1)

        #Вторая итерация получения прямой картинки
        response = requests.get('https://yandex.ru'+agg[random_number]['href'])
        print("ищем тут")
        print('https://yandex.ru'+agg[random_number]['href'])
        soup = BeautifulSoup(response.content, "html.parser")
        agg = soup.find_all('img')
        random_number = random.randint(0,len(agg)-1)
        pre_result = agg[random_number]['data-thumb']
        result = 'https:'+ pre_result
        return result


# ВК авторизация и пост на стену.
def VK_POST(LOGIN,PASS,YANDEX_SEARCH):
    vk_session = vk_api.VkApi(LOGIN,PASS)
    vk_session.auth()

    vk = vk_session.get_api()

    url_images = parser_images(YANDEX_SEARCH)
    if(url_images == False):
        print("Не взлетело")
        return False
    else:
        #Отправка картинки на стену пользователю.
        # print(vk.wall.post(message="test_wall_post_user_script",attachments='https://image.winudf.com/v2/image1/Y29tLmFuZHJvbW8uZGV2NTQ1NDExLmFwcDEwMTkxNDlfc2NyZWVuXzExXzE1NjgzOTczNTFfMDU5/screen-11.jpg?h=710&fakeurl=1&type=.jpg'))
        # Пока отправляем самому себе.
        print(url_images)
        result = vk.wall.post(message="test_wall_post_user_script",attachments=url_images)
        return result

print(VK_POST(LOGIN,INPUTPASS,YANDEX_SEARCH))
