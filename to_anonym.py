import vk_api
import random
import json
import sqlite3

token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество


class ToAnonym:
    def __init__(self, userID):
        self.userID = userID
        self.pseudonymID = None
        self.pseudonym = None

    def _main(self, message):
        keyboard = {
            "one_time": True,
            "buttons": [
                [self.button("Стоп", "negative")],
            ]}
        if len(message.split(" ")) > 1:
            if self._find_user(message.split(" ")[1]):
                method = self._send
                response = "Введите текст для получателя: " + self.pseudonym
            else:
                method = self._pseudonym
                response = "Нет такого, введите другого"

        else:
            method = self._pseudonym
            response = "Введите псевдоним:"

        return response, method, keyboard

    # получение псевдонима
    def _pseudonym(self, message):
        if self._find_user(message):
            method = self._send
            response = "Введите текст для получателя: " + self.pseudonym
        else:
            response = "Нет такого, введите другого:"
            method = self._pseudonym

        return response, method, None

    # поиск пользователя по псевдониму
    def _find_user(self, message):
        message = message.lower()
        self._connect()
        pseudonymID = self._request("SELECT id FROM pseudonyms WHERE LOWER(pseudonym) = '" + message + "'", True, False)
        if pseudonymID:
            self.pseudonymID = pseudonymID[0][0]
            self.pseudonym = self._request("SELECT pseudonym FROM pseudonyms WHERE id = " + str(self.pseudonymID) + "", True, False)[0][0]
            return True
        else:
            return  False


    # отправка сообщения
    def _send(self, message):
        try:
            sender = vk.method("users.get", {"user_ids": int(self.userID)})
            message = "ВАМ ПРИШЛО СООБЩЕНИЕ ПО ВАШЕМУ ПСЕВДОНИМУ!" \
                      "\nОтправитель: " + sender[0]['first_name'] + " " + sender[0]['last_name'] + " vk.com/id" + str(self.userID) + \
                      "\nТекст сообщения:\n ✏" + message + "✏" \
                      "\n\nP.S. Для смены псевдонима введите ПСЕВДОНИМ."

            vk.method('messages.send',
                      {'user_id': self.pseudonymID, 'message': message, 'random_id': random.getrandbits(64)})
            response = "Сообщение отправлено!"
            method = None
        except vk_api.exceptions.VkApiError:
            response = "Я не могу отправить сообщение пользователю, возможно, он добавил меня в ЧС"
            method = None

        return response, method, None

    # ------------------------------------------------------------------------------------------------------------------
    # подключение к базе данных
    def _connect(self):
        self.connect = sqlite3.connect('data/base.db')
        cursor = self.connect.cursor()
        self.cursor = cursor

    # выполнение запроса
    def _request(self, command, show, save):
        self.cursor.execute(command)
        if save:
            self.connect.commit()
        if show:
            result = self.cursor.fetchall()
            return result



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
