import vk_api
import random
import json
import sqlite3
import requests
from bs4 import BeautifulSoup

token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество


class UserInfo:

    def __init__(self, userID):
        self.userID = userID

    def _main(self, message):
        keyboard = {
            "one_time": True,
            "buttons": [
                [self.button("Стоп", "negative")],

            ]}
        userState = self._information
        response = "Укажите пользователя (ссылка/ID):"
        return response, userState, keyboard

    def _information(self, message):
        keyboard = {
            "one_time": True,
            "buttons": [
                [self.button("Стоп", "negative")],

            ]}
        userID, screen_name = self._idExtraction(message)
        response = requests.get('https://vk.com/id' + str(userID)).text
        if BeautifulSoup(response, "html.parser").find('title').text == "404 Not Found":
            userState = self._information
            response = "Неверно указан пользователь!]\n Попробуйте ещё:"

        fullName = BeautifulSoup(response, "html.parser").find('h2', {'class': 'op_header'}).text
        subscribers = BeautifulSoup(response, "html.parser").find('div', {'class': 'OwnerInfo__rowCenter'}).text.split(" ")[0]

        if not screen_name:
            screen_name = "Нет короткого имени"

        userState = "end"
        response = fullName + "\nПодписчики: " + str(subscribers) + "\nКороткое имя: " + screen_name

        return response, userState, keyboard

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _idExtraction(message):
        screen_name = None
        if message[:6] == "vk.com":
            screen_name = message[7:]
            try:
                userID = vk.method('utils.resolveScreenName', {"screen_name": message[7:]})['object_id']
            except TypeError:
                userID = message[9:]
            message = userID

        elif message[:14] == "https://vk.com":
            screen_name = message[15:]
            try:
                userID = vk.method('utils.resolveScreenName', {"screen_name": message[15:]})['object_id']
            except TypeError:
                userID = message[17:]
            message = userID

        return message, screen_name

    @staticmethod
    def button(label, color):
        return {
            "action": {
                "type": "text",
                "payload": json.dumps(""),
                "label": label
            },
            "color": color
        }
