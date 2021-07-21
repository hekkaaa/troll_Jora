import vk_api
import hashlib

print("Введите ваш логин VK")
LOGIN = input()
print("Введите пароль")
INPUTPASS = input()

# хеширование пароля
hash_object = hashlib.sha256(INPUTPASS.encode())
hex_dig = hash_object.hexdigest()

####

# ВК авторизация
vk_session = vk_api.VkApi(LOGIN, PASS)
vk_session.auth()

vk = vk_session.get_api()
#Отправка картинки на стену пользователю.
print(vk.wall.post(message="test_wall_post_user_script",attachments='https://image.winudf.com/v2/image1/Y29tLmFuZHJvbW8uZGV2NTQ1NDExLmFwcDEwMTkxNDlfc2NyZWVuXzExXzE1NjgzOTczNTFfMDU5/screen-11.jpg?h=710&fakeurl=1&type=.jpg',owner_id=196719429))