import vk_api
import random
import json
import sqlite3

token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество


class Anonymous:
    def __init__(self, userID):
        self.userID = userID

        # получение имени отправителя
        sender = vk.method("users.get", {"user_ids": int(self.userID)})
        self.first_name = sender[0]['first_name']
        self.last_name = sender[0]['last_name']
        self.lst_userIDS = []

    def _main(self, message):


        keyboard = {
            "one_time": True,
            "buttons": [
                [self.button("Стоп", "negative")],

            ]}
        dialogs = vk.method("messages.getDialogs")
        dialogsIDS = ""
        for dialog in dialogs['items']:
            self.lst_userIDS.append(dialog['message']['user_id'])
            dialogsIDS += ", " + str(dialog['message']['user_id'])

        dialogsIDS = dialogsIDS[2:]
        potential = vk.method("users.get", {"user_ids": dialogsIDS})
        users = ""
        for user in potential:
            users += user["first_name"] + " " + user["last_name"] + " - " + "vk.com/id" + str(user["id"]) + "\n"

        response = "Это функция отправки анонимных сообщений через меня. Вы пишите, я - отправляю. " \
                   "К сожалению, я не могу отправить сообщение пользователю, если у меня нет с ним " \
                   "диалога и он не подписан на меня, потому что возможности у сообществ ограничены." \
                   "\nПользователи, которым я могу отправлять сообщения:\n" + users + \
                   "\nВведите ID или ссылку пользователя, которому хотите отправить анонимное сообщение:"
        method = self._anonymous

        return response, method, keyboard

    def _anonymous(self, message):
        method = self._message
        message = self._idExtraction(message)
        try:
            keyboard = {
                "inline": True,
                "buttons": [
                    [self.button(self.first_name, "primary")],
                    [self.button(self.last_name, "primary")],
                    [self.button(self.first_name + ' ' + self.last_name, "primary")],
                    [self.button("Аноним", "positive")],
                    [self.button("Стоп", "negative")]
                ]}
            self.recipient_id = message
            # получение имени получателя
            recipient = vk.method("users.get", {"user_ids": int(message)})
            response = "Получатель: " + recipient[0]['first_name'] + " " + recipient[0]['last_name'] + \
                       "\nКак указать вас получателю в качестве отправителя?"
            if int(message) not in self.lst_userIDS:
                response = "ЭТОГО ПОЛЬЗОВАТЕЛЯ НЕТ В СПИСКЕ ДОСТУПНЫХ, ПОЭТОМУ НЕ ФАКТ ЧТО Я СМОГУ ОТПРАВИТЬ ЕМУ СООБЩЕНИЕ!\n" + response
        except vk_api.exceptions.VkApiError:
            keyboard = {
                "one_time": True,
                "buttons": [
                    [self.button("Стоп", "negative")],
                ]}
            method = self._anonymous
            response = "Неверный ID!\nПопробуйте ещё:"
        except ValueError:
            keyboard = {
                "one_time": True,
                "buttons": [
                    [self.button("Стоп", "negative")],

                ]}
            method = self._anonymous
            response = "Хватит баловаться!\nДавай по новой:"

        return response, method, keyboard

    def _message(self, message):
        keyboard = {
            "one_time": True,
            "buttons": [
                [self.button("Стоп", "negative")],

            ]}
        method = self._send
        response = "Введите сообщение для получателя:"

        if message.lower() == self.first_name.lower():
            self.who = self.first_name
        elif message.lower() == self.last_name.lower():
            self.who = self.last_name
        elif message.lower() == self.first_name.lower() + " " + self.last_name.lower():
            self.who = self.first_name + ' ' + self.last_name
        elif message.lower() == "аноним":
            self.who = "аноним"
        else:
            response = "Вы не " + message + ".\nПишите без ошибок!"
            method = self._message

        return response, method, keyboard

    def _send(self, message):
        keyboard = None
        if message == "":
            keyboard = {
                "one_time": True,
                "buttons": [
                    [self.button("Стоп", "negative")],

                ]}
            response = "Всё-таки надо что-то написать!"
            method = self._send
        else:
            method = None
            self._connect()
            pseudonym = self._request("SELECT pseudonym FROM pseudonyms WHERE id = " + str(self.userID) + "", True, False)
            if pseudonym:
                pseudonym = pseudonym[0][0]
                keyboard_recipient = {
                    "inline": True,
                    "buttons": [[self.button("Ответить " + pseudonym, "positive")]]}
                keyboard_recipient = json.dumps(keyboard_recipient, ensure_ascii=False).encode('utf-8')
                keyboard_recipient = str(keyboard_recipient.decode('utf-8'))
            else:
                pseudonym = "У этого анонима нет псевдонима!"
                keyboard_recipient = None
            try:
                message = "ВАМ ПРИШЛО АНОНИМНОЕ СООБЩЕНИЕ!" \
                          "\nОтправитель: " + self.who + \
                          "\nПсевдоним: " + pseudonym + \
                          "\nТекст сообщения:\n ✏" + message + "✏" \
                          "\nP.S. Для отправки анонимных сообщений введите АНОНИМ." \
                          "\nP.S.S. Для ответа анониму введите ОТВЕТИТЬ %псевдоним%." \
                          "\nP.S.S.S Для создания псевдонима введите ПСЕВДОНИМ."
                vk.method('messages.send', {'user_id': self.recipient_id, 'message': message, 'random_id': random.getrandbits(64), "keyboard": keyboard_recipient})
                response = "Сообщение отправлено!"
            except vk_api.exceptions.VkApiError:
                response = "Возможно вы указали пользователя не из списка доступных, или этот пользователь меня заблокировал." \
                           "\nВозвращение в режим собеседника!"

        return response, method, keyboard

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

    # переводит все буквы после '. ' в верхний регистр
    @staticmethod
    def _txt(text):
        string = ""
        for sentence in text.split(". "):
            string += sentence.capitalize() + ". "
        string = string[0:-2]
        
        return string

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

    # получение id профиля
    @staticmethod
    def _idExtraction(message):
        if message[:6] == "vk.com":
            try:
                userID = vk.method('utils.resolveScreenName', {"screen_name": message[7:]})['object_id']
            except TypeError:
                userID = message[9:]
            message = userID

        elif message[:14] == "https://vk.com":
            try:
                userID = vk.method('utils.resolveScreenName', {"screen_name": message[15:]})['object_id']
            except TypeError:
                userID = message[17:]
            message = userID

        return message
