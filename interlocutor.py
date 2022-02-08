import sqlite3
import json


class Interlocutor:
    def __init__(self, peerID):
        self.peerID = peerID

    def _main(self, message, old):  # режим беседы (изначальный режим)
        message = message.lower()
        message = self._punctuation(message)
        key_word = None
        response = self._phrase(message)
        if response is None:
            for word in message.split(" "):
                key_word = self._pars(word)
                if key_word is not None:
                    break
            response = self._answer(old, key_word)

        return response, key_word

    def _pars(self, word):
        self._connect()
        columns = self._request("pragma table_info(words)")
        columns.pop(0)

        group_name = None
        for column in columns:
            strings = self._request("SELECT " + column[1] + " FROM words")
            for string in strings:
                if string[0] is None:
                    break
                if string[0] == word:
                    group_name = column[1]
                    return group_name

        return group_name

    def _answer(self, old, new):

        if old is None:
            old = "неизвестно"
        if new is None:
            new = "неизвестно"

        self._connect()
        response = self._request("SELECT " + new + " FROM answers WHERE column = '" + old + "'")
        response = response[0][0]

        if response is None:
            response = "Даже не знаю что ответить"

        return response

    def _phrase(self, message):
        message = message.lower()
        self._connect()
        phrases = self._request("SELECT input FROM phrases")

        response = None
        message = self._punctuation(message)

        for phrase in phrases:
            if message == phrase[0]:
                response = self._request("SELECT output FROM phrases WHERE input = '" + message + "'")
                response = response[0][0]
                break

        return response

    @staticmethod
    def _punctuation(message):
        punctuations = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", ",", ".", "?", "|", "/", ":", ";"]
        for p in punctuations:
            if p in message:
                message = message.replace(p, '')
        return message

    def _connect(self):
        self.connect = sqlite3.connect('data/base.db')
        cursor = self.connect.cursor()
        self.cursor = cursor

    # выполнение запроса
    def _request(self, command):
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return result
