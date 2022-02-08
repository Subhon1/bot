import sqlite3
import json


class Pseudonym:
    def __init__(self, userID):
        self.userID = userID

    def _main(self, message):
        self._connect()
        response = "Псевдоним отправителя отображается у получателей анонимных сообщений." \
                   "\nПсевдоним не рассекречивает профиль, он лишь даёт возможность получателю анонимного сообщения ответить отправителю по его псевдониму." \
                   "\nЕсли вы хотите что бы на ваше анонимное сообщение могли ответить, то создайте псевдоним!"
        pseudonym = self._request("SELECT pseudonym FROM pseudonyms WHERE id = " + str(self.userID), True, False)
        if pseudonym:
            method = self._pseudonym_edit
            response += "\nВаш псевдоним: " + pseudonym[0][0] + "\nВведите новый псевдоним:"
            # бронирование ячейки для редактирования
            self._request("UPDATE pseudonyms SET pseudonym = '*' WHERE id = " + str(self.userID), False, True)
        else:
            method = self._pseudonym_add
            response += "\nВведите псевдоним, который будет отображаться у получателей анонимных сотобщений:"

        return response, method, None

    def _pseudonym_add(self, message):
        if len(message.split(" ")) == 1:
            if self._request("SELECT pseudonym FROM pseudonyms WHERE LOWER(pseudonym) = '" + message.lower() + "'", True, False):
                method = self._pseudonym_add
                response = "Этот псевдоним занят, введите другой:"
            elif len(message) > 20:
                method = self._pseudonym_add
                response = "Псевдоним должен содержать не более 20-ти символов, попробуйте ещё:"
            else:
                self._connect()
                self._request("INSERT INTO pseudonyms (id, pseudonym) VALUES (" + str(self.userID) + ", '" + message + "')", False, True)
                method = None
                response = "Ваш псевдоним установлен: " + message
        else:
            method = self._pseudonym_add
            response = "Псевдоним должен содержать не более одного слова, попробуйте ещё:"

        return response, method, None

    def _pseudonym_edit(self, message):
        if len(message.split(" ")) == 1:
            if self._request("SELECT pseudonym FROM pseudonyms WHERE LOWER(pseudonym) = '" + message.lower() + "'", True, False):
                method = self._pseudonym_edit
                response = "Этот псевдоним занят, введите другой:"
            elif len(message) > 20:
                method = self._pseudonym_edit
                response = "Псевдоним должен содержать не более 20-ти символов, попробуйте ещё:"
            else:
                self._connect()
                self._request("UPDATE pseudonyms SET pseudonym = '" + message + "' WHERE id = " + str(self.userID), False, True)
                method = None
                response = "Ваш псевдоним изменён: " + message
        else:
            method = self._pseudonym_edit
            response = "Псевдоним должен содержать не более одного слова, попробуйте ещё:"

        return response, method, None

    """
    САМОСТОЯТЕЛЬНЫЕ МЕТОДЫ
        """
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
