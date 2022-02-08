from vk_api import VkApi
import random
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


token = "4988a35fd19c733bbe964d214bc048ff006cace0557bbdfe740ae6dde046488654b96e9be18243824ebd2"  # API-ключ
#token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = VkApi(token=token)  # авторизуемся как сообщество
longpoll = VkLongPoll(vk)  # работа с сообщениями


def button(label, color):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(""),
            "label": label,
        },
        "color": color
    }


def _write_msg(peerID, response, keyboard=None):
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))

    vk.method('messages.send', {'user_id': peerID, 'message': response, 'random_id': random.getrandbits(64), 'keyboard': keyboard})
    print("RESPONSE: " + response + "\n________________________________\n")
    return


dialogs = vk.method("messages.getDialogs")
declaration = "Доброго времени суток, кожанные мешки. Я был обновлён:"\
                  "\n- Добавлен пункт 'Фразы' в режиме обучения;"\
                  "\n- Добавлена возможность общения в беседах;"\
                  "\n- Добавлена команда для бесед '/Перевод' - для общения разноязычных пользователей между собой;"\
                  "\n- Добавлена клавиатура быстрых ответов;"\
                  "\n- Произведены реструктурирование и оптимизация бота, в следствии чего было внесено множество мелких изменений;"\
                  "\n- Теперь в диалогах вообще не нужно прописывать '/' (слэш), он нужен только в беседах."\
                  "\nДля получения справки введите 'Помощь'."
keyboard = {
                "inline": True,
                "buttons": [
                    [
                        button("Учить", "primary"),
                        button("Аноним", "primary"),
                    ], [button("Помощь", "negative")]
                ]}

for i in dialogs['items']:
    try:
        print(i['message']['user_id'])
        _write_msg(i['message']['user_id'], declaration, keyboard)
    except vk_api.exceptions.VkApiError:
        print("BLOCK -", i['message']['user_id'])
        continue
