import json
from datetime import datetime
import urllib.request
import vk_api
import random
import os


token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество


class Statistic:
    def __init__(self, userID):
        self.userID = userID

    def _main(self, message, items):
        response = "Отправте мне файл переписки в формате .json. \nО том, как этот файл получить, читайте в статье 'Nostalgia'."
        method = self._analyze
        return response, method, None

    def _analyze(self, message, items):
        method = None
        try:
            path = 'data\\chats\\' + items['name']
            urllib.request.urlretrieve(items['URL'], path)
            with open(path, 'r', encoding='utf-8') as f:  # открыли файл с данными
                dialog = json.load(f)


            #path = os.path.join(os.path.abspath(os.path.dirname(__file__)), path)
            #os.remove(path)

            message = dict()
            for i in range(len(dialog)):
                message[i] = {'id': str(dialog[i]['from_id']),
                              'date': datetime.fromtimestamp(int(dialog[i]['date'])).strftime('%Y-%m-%d %H:%M:%S'),
                              'text': self._punctuation(dialog[i]['body']).lower()}

            users = dict()
            for i in message:
                if message[i]['id'] in users:
                    users[message[i]['id']]['count'] += 1
                    users[message[i]['id']]['messages'].append(message[i]['text'])
                else:
                    user = vk.method("users.get", {"user_ids": int(message[i]['id'])})
                    first_name = user[0]['first_name']
                    last_name = user[0]['last_name']
                    users[message[i]['id']] = {'count': 1, 'messages': [message[i]['text']], 'name': first_name + " " + last_name}

            response = "количество сообщений:\n&#12288;"
            for i in users:
                response += users[i]['name'] + ' - ' + str(users[i]['count']) + ' | '
            response = response[:len(response)-3]

            vk.method('messages.send', {'user_id': self.userID, 'message': response, 'random_id': random.getrandbits(64)})
            response = ""

            words = dict()  # словарь: ид_пользователя - слово - количество
            for user in users:
                if user not in words:
                    words[user] = {}
                    for message in users[user]['messages']:
                        for word in message.split(" "):
                            if len(word) > 3:
                                if word in words[user]:
                                    words[user][word] += 1
                                else:
                                    words[user][word] = 1

            for user in words:
                words[user] = {k: v for k, v in sorted(words[user].items(), key=lambda item: item[1])}

            response += "количество слов:\n&#12288;"
            for user in words:
                response += users[user]['name'] + ' - ' + str(len(words[user])) + ' | '
            response = response[:len(response)-3]

            vk.method('messages.send', {'user_id': self.userID, 'message': response, 'random_id': random.getrandbits(64)})
            response = ""

            lWords = dict()  # отсортированные слова
            for user in words:
                lWords[user] = {'words': [], 'count': []}
                for word in words[user]:
                    lWords[user]['words'].append(word)
                    lWords[user]['count'].append(words[user][word])

            response += "топ 10 используемых слов:"
            for user in lWords:
                sizeList = len(lWords[user]['words']) - 1
                response += "\n&#12288;" + users[user]['name'] + ':\n'
                for k in range(sizeList+1):
                    response += "&#12288;&#12288;" + lWords[user]['words'][sizeList - k] + " - " + str(lWords[user]['count'][sizeList - k]) + "\n"
                    if k > 8:
                        break
                vk.method('messages.send', {'user_id': self.userID, 'message': response, 'random_id': random.getrandbits(64)})
                response = ""

            response = "Готово!"
        except KeyError:
            response = "Нужно отправить мне файл в формате .json"
            method = self._analyze
            keyboard = None
        except:
            response = "  файл! Отправте другой:"
            method = self._analyze

        return response, method, None

    @staticmethod
    def _punctuation(message):
        punctuations = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", ",", ".", "?", "|", "/", ":", ";", "\n"]
        for p in punctuations:
            if p in message:
                message = message.replace(p, '')
        return message
