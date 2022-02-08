import requests
import sqlite3
import vk_api
import json

token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество


class Translate:
    def __init__(self, chatID):
        self.chatID = chatID
        self.languages = {}
        self.response = None
        self.url = "https://microsoft-translator-text.p.rapidapi.com/translate"
        self.key = "b1e53e4fcamshf8f53a3e387486cp183572jsn5216e8fdfb51"
        self.urlYand = "https://google-translate1.p.rapidapi.com/language/translate/v2"
        self.keyYand = "tb1e53e4fcamshf8f53a3e387486cp183572jsn5216e8fdfb51"
        self.language = None
        self.usersID = {}
        self.buttons = None

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

    def _main(self, message, userID):
        method = self._translate
        response = "Введите язык, на который следует переводить текст ваших сообщений.\n" \
                   "Для вывода списка доступных языков введите ЯЗЫКИ."

        self._connect()
        langs = self._request("SELECT language FROM languages ORDER BY id")
        codes = self._request("SELECT code FROM languages ORDER BY id")
        for i in range(len(langs)):
            self.languages[langs[i][0]] = codes[i][0]

        buttons = [[]]
        i = -1
        k = 0
        for lang in self.languages:
            i += 1
            if i == 3:
                i = 0
                buttons.append([])
                k += 1

            buttons[k].append(self.button(lang.capitalize(), "primary"))

        self.buttons = buttons
        self.response = "Доступные языки:"
        keyboard = {
            "one_time": True,
            "buttons": buttons}
        return response, method, keyboard

    def _translate(self, message, userID):
        keyboard = {
            "one_time": True,
            "buttons": [[self.button("Языки", "primary")]]}
        message = message.lower()
        method = self._translate
        userName = vk.method("users.get", {"user_ids": int(userID)})[0]['first_name']
        if message == "языки":
            response = self.response
            keyboard = {
                "one_time": True,
                "buttons": self.buttons}
        elif message in self.languages:
            response = userName + ", вам установлен язык: " + message.capitalize()
            self.usersID[userID] = message
        else:
            if userID in self.usersID:
                language = self.languages[self.usersID[userID]]
                try:
                    querystring = {"to": language, "api-version": "3.0", "profanityAction": "NoAction", "textType": "plain"}
                    payload = "[\r{\r\"Text\": \"" + str(message) + "\"\r}\r]"
                    headers = {
                        'content-type': "application/json",
                        'x-rapidapi-key': self.key,
                        'x-rapidapi-host': "microsoft-translator-text.p.rapidapi.com"
                    }

                    response = requests.request("POST", self.url, data=payload.encode(), headers=headers, params=querystring).json()
                    response = userName + ": " + response[0]["translations"][0]["text"]
                except:
                    try:
                        headers = {
                            "content-type": "application/x-www-form-urlencoded",
                            'accept-encoding': 'application/gzip',
                            'x-rapidapi-host': 'google-translate1.p.rapidapi.com',
                            'x-rapidapi-key': 'b1e53e4fcamshf8f53a3e387486cp183572jsn5216e8fdfb51'
                        }
                        data = {"q": message, "target": language}
                        response = requests.request("POST", self.urlYand, data=data, headers=headers).json()
                        print(response)
                        response = userName + ": " + response['data']["translations"][0]["translatedText"]
                    except:
                        response = "Извините, лимит на Таджикский язык закончился"

            else:
                response = userName + ", вы не выбрали язык! Выбирайте:"
                keyboard = {
                    "one_time": True,
                    "buttons": self.buttons}

        return response, method, keyboard

    """
    САМОСТОЯТЕЛЬНЫЕ МЕТОДЫ
    """
    def _connect(self):
        self.connect = sqlite3.connect('data/base.db')
        cursor = self.connect.cursor()
        self.cursor = cursor

    # выполнение запроса
    def _request(self, command):
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return result

    @staticmethod
    def _punctuation(message):
        punctuations = ["/", "\'"]
        for p in punctuations:
            if p in message:
                message = message.replace(p, '')

        return message
