import vk_api
import random
import threading
import json
import requests
import time
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# импорт файлов
from interlocutor import Interlocutor
from anonymous import Anonymous
from learn import Learn
from translate import Translate
from pseudonym import Pseudonym
from to_anonym import ToAnonym
from book import Book
from administrator import Administrator
#from user_info import UserInfo
from statistic import Statistic
from imitation import Imitation

# standalone - 43921a9043921a9043921a90a643e4d9564439243921a9023d689d2040a346c0d86996d
# t6qu8C0t9RvpMqvyo2bP


def button(label, color):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(""),
            "label": label,
        },
        "color": color
    }


def _write_msg(peerID, response, chat, keyboard=None):
    peer = None
    if chat == "(PRIVATE)":
        peer = 'user_id'
    elif chat == "(PUBLIC)":
        peer = 'peer_id'

    if keyboard:
        keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
        keyboard = str(keyboard.decode('utf-8'))

    vk.method('messages.send', {peer: peerID, 'message': response, 'random_id': random.getrandbits(64), 'keyboard': keyboard})
    print("RESPONSE: " + response + "\n________________________________\n")

    """
    проверка на ошибки (при доработке убрать кавычки)
    try:
        vk.method('messages.send', {peer: peerID, 'message': response, 'random_id': random.getrandbits(64), 'keyboard': keyboard})
        print("RESPONSE: " + response + "\n________________________________\n")
    except vk_api.exceptions.VkApiError:
        print("BLOCK RESPONSE: " + response + "\n________________________________\n")   
    """
    return


def _robotKeys(message):
    keyboard = None
    if message.lower() == "начать":
        keyboard = keyboardSamples["начать"]
    elif message.lower() == "собеседник":
        keyboard = keyboardSamples["собеседник"]
    elif message.lower() == "анонимус":
        keyboard = keyboardSamples["анонимус"]
    elif message.lower() == "ностальгия":
        keyboard = keyboardSamples["ностальгия"]

    return keyboard


token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество
longpoll = VkLongPoll(vk)  # работа с сообщениями
id_group = 164076806

vk_session = vk_api.VkApi(token=token)
longpollBot = VkBotLongPoll(vk_session, id_group)
vkBot = vk_session.get_api()

userStates = {1: ['interlocutor'],  # разбитие функций на типы, которые отличаются аргументами
              2: ['learn', 'anonymous', 'pseudonym', 'toAnonym', 'book', 'administrator', 'userInfo'],
              3: ['statistic', 'imitation']}
commandsUser = {"учить": Learn, "аноним": Anonymous, "псевдоним": Pseudonym, "ответить": ToAnonym, "книга": Book, "админ": Administrator, 'статистика': Statistic, "имитация": Imitation}  # список комманд
wordsUser = {"учить": 'learn', "аноним": 'anonymous', "псевдоним": 'pseudonym', "ответить": 'toAnonym', "книга": 'book', "админ": 'administrator', "инфа": 'userInfo', 'статистика': 'statistic', 'имитация': "imitation"}  # список комманд


botStates = {1: ['interlocutor'], 2: ['translate']}
commandsBot = {"перевод": Translate}
wordsBot = {'перевод': 'translate'}

users = []  # список ID пользователей
chats = []  # список ID чатов

keyboardSamples = {  # шаблоны робоклавиатур
    "начать": {
                "inline": True,
                "buttons": [
                    [
                        button("Собеседник", "positive"),
                        button("Анонимус", "primary"),
                        button("Ностальгия", "negative")
                    ],
                    [button("Книга жалоб и предложений", "secondary")],
                    [button("Помощь", "secondary")]
                ]},
    "собеседник": {
                "inline": True,
                "buttons": [
                    [
                        button("учить", "primary"),
                    ],
                    [button("Помощь", "secondary")]
                ]},
    "анонимус": {
                "inline": True,
                "buttons": [
                    [
                        button("Аноним", "primary"),
                        button("Псевдоним", "primary"),
                        button("Ответить", "primary"),
                    ],
                    [button("Помощь", "secondary")]
                ]},
    "ностальгия": {
                "inline": True,
                "buttons": [
                    [
                        button("статистика", "primary"),
                        button("имитация", "primary"),
                    ],
                    [button("Помощь", "secondary")]
                ]}}


def _response(peerID):
    while True:
        try:
            for event in longpollBot.listen():
                newID = event.object.peer_id
                message = event.object.text.replace("\\", "")
                message = message.replace("\"", "")
                message = message.replace("'", "")
                items = dict()
                attachments = event.object.attachments
                if len(attachments) > 0:
                    attachments = attachments[0]
                    if 'doc' in attachments:
                        items['type'] = attachments['doc']['ext']
                        items['URL'] = attachments['doc']['url']
                        items['name'] = attachments['doc']['title']

                if event.from_user:  # from user
                    print("(PRIVATE) ID thread: " + str(peerID) + " | ID user: " + str(newID) + " | message: " + message + "\n")

                    if peerID == newID:
                        return message, items
                    elif (newID not in users) and (peerID == 0):
                        users.append(newID)
                        cls = Interlocutor(peerID)
                        method = cls._main
                        thread = threading.Thread(target=_distributor, args=(newID, message, method, items))
                        thread.start()
                        continue

                elif event.from_chat:  # from chat
                    message = message[1:]
                    userID = event.object.from_id
                    print("(PUBLIC) ID thread: " + str(peerID) + " | ID chat: " + str(newID) + " | message: " + message + "\n")

                    if peerID == newID:
                        return message, userID
                    elif (newID not in chats) and (peerID == 0):
                        chats.append(newID)
                        cls = Interlocutor(peerID)
                        method = cls._main
                        thread = threading.Thread(target=_distributorBot, args=(newID, message, method, userID))
                        thread.start()
                        continue
        except requests.exceptions.ConnectionError:
            fileLog = open("log.txt", "a")
            fileLog.write("ConnectError " + str(peerID) + "\n")
            fileLog.close()
            print("(ConnectError) ID thread: " + str(peerID) + "\n")
            time.sleep(1)
            continue
        except requests.exceptions.ReadTimeout:
            fileLog = open("log.txt", "a")
            fileLog.write("ReadTimeout " + str(peerID) + "\n")
            fileLog.close()
            print("(ReadTimeout) ID thread: " + str(peerID) + "\n")
            time.sleep(1)
            continue


def _distributor(userID, message, method, items, response=None, state='interlocutor', old=None):
    while True:
        if message.lower() == "помощь":
            message = "начать"

        # применение робоклавиатуры
        keyboard = _robotKeys(message)

        # кодовые сообщения
        if message == "":
            message = "code2"
        elif message.lower() == "стоп":
            if state != 'interlocutor' and state is not None:
                message = "code1"
                method = None  # если ошибка: method = ''
                state = None

        # возвращение в режим собеседника
        if not state:
            state = 'interlocutor'
            cls = Interlocutor(userID)
            method = cls._main

        # в режиме собеседника доступна инициализация перехода в другой режим
        if state == 'interlocutor':
            command = message.lower().split(" ")[0]
            if command in commandsUser:
                state = wordsUser[command]
                cls = commandsUser[command](userID)
                method = cls._main

        # набор переменных и аргументов для каждого типа пользовательской функции
        if state in userStates[1]:
            response, old = method(message, old)
        elif state in userStates[2]:
            response, method, keyboard = method(message)
        elif state in userStates[3]:
            response, method, keyboard = method(message, items)

        if method is None:
            state = None
            response = response + "\nВозвращение в режим собеседника"

        _write_msg(userID, response, "(PRIVATE)", keyboard)

        message, items = _response(userID)


def _distributorBot(chatID, message, method, userID, state='interlocutor', response=None, old=None):
    while True:
        if message[:25] == "club164076806|@sss_knife]":
            message = message[26:]
        elif message[:21] == "club164076806|I, Bot]":
            message = message[22:]

        keyboard = None
        if message.lower() == "помощь":
            message = "начать"
        if message.lower() == "начать":
            keyboard = {
                "inline": True,
                "buttons": [
                    [button("Перевод", "primary")],
                    [button("Помощь", "positive")]
                ]}

        # кодовые сообщения
        if message == "":
            keyboard = {
                "inline": True,
                "buttons": [[button("Помощь", "positive")]]}
            message = "code2"
        elif message.lower() == "стоп":
            if state != 'interlocutor':
                message = "code1"
                state = 'end'

        # возвращение в режим собеседника
        if state == 'end':
            state = 'interlocutor'
            cls = Interlocutor(chatID)
            method = cls._main

        # в режиме собеседника доступна инициализация перехода в другой режим
        if state == 'interlocutor':
            command = message.lower().split(" ")[0]
            if command in commandsBot:
                state = wordsBot[command]
                cls = commandsBot[command](chatID)
                method = cls._main

        # набор переменных и аргументов для каждого типа пользовательской функции
        if state in botStates[1]:
            response, old = method(message, old)
        elif state in botStates[2]:
            response, method, keyboard = method(message, userID)

        _write_msg(chatID, response, "(PUBLIC)", keyboard)  # обращение к функции отправки сбщ
        message, userID = _response(chatID)


_response(0)
