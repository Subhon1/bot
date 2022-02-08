import json
import sqlite3

class Book:
    def __init__(self, userID):
        self.userID = userID

    def _main(self, message):
        keyboard = {
            "one_time": True,
            "buttons": [
                [self.button("Стоп", "negative")],

            ]}
        method = self._statement
        response = "Введите своё заявление - жалобу или предложение. Будет замечательно, если вы предложите свою идею. Каждая идея будет рассмотрена к реализации.\n" \
                   "Заявление не должно содержать больше 100 символов, по этому пишите кратко! Мой администратор напишет тому пользователю, чьё заявление понравилось, для дальнейшего обсуждения.\nВведите заявление:"

        return response, method, keyboard

    def _statement(self, message):
        keyboard = None
        method = None
        response = "Ваше заявление добавлено!\nВозвращение в режим собеседника!"
        messageLen = len(message)
        if messageLen > 100:
            keyboard = {
                "one_time": True,
                "buttons": [
                    [self.button("Стоп", "negative")],

                ]}
            sumbolLst = ["11", "12", "13", "14", "15", "16", "17", "18", "19"]
            if str(messageLen)[-1] == "0" or str(messageLen)[-2] + str(messageLen)[-1] in sumbolLst:
                sumbolStr = "символов"
            elif str(messageLen)[-1] == "1":
                sumbolStr = "символ"
            elif int(str(messageLen)[-1]) < 5:
                sumbolStr = "символа"
            else:
                sumbolStr = "символов"

            method = self._statement
            response = "Вы не уместились в лимит, ваше заявление содержит " + str(messageLen) + " " + sumbolStr + "! Попробуйте уместиться в 100 символов:"
        else:
            self._connect()
            self._request("INSERT INTO book (id, statement) VALUES (" + str(self.userID) + ", '" + message + "')", False, True)

        return response, method, keyboard

    # ------------------------------------------------------------------------------------------------------------
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