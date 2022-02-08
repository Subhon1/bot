import sqlite3
import random
import json


class Learn:
    def __init__(self, peerID):
        self.peerID = peerID
        self.group = None  #
        self.wordError = None  #
        self.ind = 0  #
        self.flag = False  #
        self.old_message = None  #
        self.new_message = None  #
        self.answer = None
        self.cursor = None  # переменная, хранящая курсоор базы даных
        self.connect = None  # функция подключения к базе данных
        self.word = None  # слово, которое может быть заменено
        self.phrase = None  # переменная, хранящая фразу для добавления фразы-ответа
        self.keyboard = None
        self.keymode = {
            "inline": True,
            "buttons": [
                [
                    self.button("Слова", "primary"),
                    self.button("Ответы", "primary"),
                ], [
                    self.button("Группы", "primary"),
                    self.button("Фразы", "primary")
                ], [self.button("Стоп", "negative")]
            ]}
        self.keyback = {
                    "one_time": True,
                    "buttons": [[self.button("Назад", "negative")]]}

    """
    ВЫБОР РЕЖИМА ОБУЧЕНИЯ
        """
    # вступление
    def _main(self, message):
        keyboard = self.keymode

        response = "Чему ты будешь меня обучать?"
        method = self._mode
        return response, method, keyboard

    # выбор режима обучения
    def _mode(self, message):
        keyboard = self.keymode
        message = message.lower()
        if message == "слова":
            method = self._words

            self._connect()
            groups = self._request("pragma table_info(words)", True, False)
            groups.pop(0)

            response = "В русском языке очень много слов с похожими значениями, " \
                       "в том числе одни и те же слова с разными склонениями, " \
                       "поэтому они были разделены на группы. \nВыбери группу слов:"

            buttons = []

            for group in groups:
                response += "\n- " + str(group[1]).upper()
                buttons.append([self.button(str(group[1]), 'positive')])

            buttons.append([self.button('Назад', 'negative')])
            keyboard = {
                "one_time": True,
                "buttons": buttons}

        elif message == "ответы":
            response = self._find_null()

            if self.flag:
                tmp = self._main(None)
                method = tmp[1]
                response = response + "Следует добавить новые группы\n" + tmp[0]
            else:
                method = self._answers
                response = "Я ответаю пользователю на основе двух сотобщений: на предыдущем сообщении пользователя и на новом (Схема: Предыдущее сообщение пользователя + Новое сообщение пользователя -> ответ бота)." \
                           "\nДа, я запоминаю что мне написали в предыдущем сообщении и анализирую что мне написали в новом сообщении." \
                           "\nТвоя задача - учить меня, как отвечать пользователям." \
                           "\nЕщё я разделяю сообщения по темам, следовательно я буду спрашивать тебя, к примеру, как я должен отвечать если предыдущее сообщение пользователя относится к теме Приветствие, а новое сообщение пользователя относиться к теме Прощание." \
                           "\nДля редактирования ответа, нужно ввести 'редактировать %тема_предыдущего_сообщения% %тема_нового_сотобщения%', например 'редактировать приветствие прощание'." \
                           "\nВремя занятий началось!" \
                           "\nЧто мне следует ответить, если:\n" + response

                keyboard = self.keyback

        elif message == "группы":
            method = self._groups
            self._connect()
            groups = self._request("pragma table_info(words)", True, False)
            groups.pop(0)
            response = "Группы хранят в себе слова похожие по значению. Вот имеющиеся группы на данный момент:"
            for group in groups:
                response += "\n- " + group[1]

            response += "\nСоздавай группы только на конкретные темы, " \
                        "не следует создавать группы на малоизвестные темы. " \
                        "Удалить группу или изменить её название ты не сможешь, " \
                        "для этого обратись к администратору." \
                        "\nСОЗДАТЬ ГРУППУ?"
            keyboard = {
                "inline": True,
                "buttons": [
                    [self.button("Создать группу", "primary")],
                    [self.button("Назад", "negative")]
                ]}
            self.keyboard = keyboard

        elif message == "фразы":
            method = self._phrases_inp

            response = "В отличие от ОТВЕТОВ, ответы на отдельные ФРАЗЫ основываются только на одном сообщении пользователя." \
                       "\n(Схема: НОвое соообщение пользователя -> Ответ бота)." \
                       "\nДля того что бы изменить Фразу-Ответ, нужно ввести уже знакомую мне фразу." \
                       "\nВремя занятий началось!" \
                       "\nВведи текст сообщения, на которое я должен ответить:"

            keyboard = self.keyback
        else:
            response = "Не понял, повтори!"
            method = self._mode

        return response, method, keyboard

    """
    СЛОВА
        """
    # есть ли такая группа в базе
    def _words(self, message):
        message = message.lower()
        if message == "назад":
            tmp = self._main(None)
            method = tmp[1]
            response = "Возвращение в меню выбора.\n" + tmp[0]
            keyboard = self.keymode
        else:
            keyboard = self.keyboard
            self._connect()
            groups = self._request("pragma table_info(words)", True, False)

            groups = self._extraction(groups, 1)
            if message in groups:
                self.group = message
                method = self._words_add
                response = "\nОтправляй мне только частоиспользуемые слова, которые " \
                           "относятся к той группе которую ты выбрал. Например, к " \
                           "группе ПРИВЕТСТВИЕ относятся слова: Привет, Здарова, Hello." \
                           "\nЕсли ты отправил мне неправильное слово или слово с ошибкой, " \
                           "тогда введи то слово, которое хочешь исправить." \
                           "\nВремя занятий началось!" \
                           "\nВводи слова относящиеся к группе " + self.group.upper() + ":"
                keyboard = self.keyback
            else:
                method = self._words
                response = "Такой группы нет!"

        return response, method, keyboard

    # добавление слов
    def _words_add(self, message):
        keyboard = self.keyback
        message = message.lower()
        method = self._words_add
        if message == "назад":
            tmp = self._main(None)
            method = tmp[1]
            response = "Возвращение в меню выбора.\n" + tmp[0]
            keyboard = self.keymode
        elif len(message.split(" ")) == 1:
            self._connect()
            words = self._request("SELECT " + self.group + " FROM words", True, False)
            response = "Слово добавлено!"
            flag = True
            ind = 1
            tmp = self._find_group(message)
            if tmp == self.group or tmp is None:
                for word in words:
                    if message == word[0]:
                        self.word = message
                        # бронирование ячейки
                        self._request("UPDATE words SET " + self.group + " = '*' WHERE " + self.group + " = '" + message + "'", False, True)
                        response = "Введи правильное слово вместо слова '" + message + "':"
                        method = self._words_edit
                        self.wordError = message
                        flag = False
                        self.ind = ind
                        keyboard = None
                        break
                    elif word[0] is None:
                        self._request("UPDATE words SET " + self.group + " = '" + message + "' WHERE  id = " + str(ind), False, True)
                        response = "Слово добавлено!"
                        flag = False

                        break
                    ind += 1
            else:
                response = "Это слово относится к группе " + tmp.upper() + ".\nВведи другое слово:"
                flag = False
            if flag:
                self._request("INSERT INTO words (" + self.group + ") VALUES ('" + message + "')", False, True)
        else:
            response = "Введи не менее и не более одного слова!"

        return response, method, keyboard

    # изменение слова
    def _words_edit(self, message):
        keyboard = None
        message = message.lower()
        if len(message.split(" ")) == 1:
            tmp = self._find_group(message)
            if tmp is None:
                self._connect()
                method = self._words_add
                self._request("UPDATE words SET " + self.group + " = '" + message + "' WHERE id = " + str(self.ind), False, True)
                response = "Слово '" + self.wordError + "' изменено на слово '" + message + "'."
                keyboard = self.keyback

            else:
                method = self._words_edit
                response = "Это слово относится к группе " + tmp.upper() + ".\nВведи другое слово:"
        else:
            method = self._words_edit
            response = "Введи не менее и не более одного слова."

        return response, method, keyboard

    """
    ОТВЕТЫ
        """
    # добавление ответов
    def _answers(self, message):
        keyboard = self.keyback
        self._connect()
        method = self._answers
        if message.lower() == "назад":
            tmp = self._main(None)
            method = tmp[1]
            self._request("UPDATE answers SET " + self.group + " = null WHERE id = " + str(self.ind), False, True)
            response = "Возвращение в меню выбора.\n" + tmp[0]
            keyboard = self.keymode
        elif message.lower().split(" ")[0:1][0] == "редактировать":
            message = message.lower()

            # удаление бронирования ячейки для добавления ответа
            self._request("UPDATE answers SET " + self.group + " = null WHERE id = " + str(self.ind), False, True)

            if len(message.split(" ")) == 3:
                old_message = message.split(" ")[1]
                new_message = message.split(" ")[2]
                if not self._request("SELECT name FROM pragma_table_info('answers') WHERE name = '" + old_message + "'", True, False) or not self._request("SELECT column FROM answers WHERE column = '" + new_message + "'", True, False):
                    response = "Таких тем я не знаю.\nПродолжаем...\n" + self._find_null()
                else:
                    self.old_message = old_message
                    self.new_message = new_message
                    answer = self._request("SELECT " + new_message + " FROM answers WHERE column = '" + old_message + "'", True, False)

                    # бронирование ячейки для изменения ответа
                    self._request("UPDATE answers SET " + new_message + " = '*'  WHERE  column = '" + old_message + "'", False, True)
                    self.answer = answer[0][0]
                    if self.answer is None:
                        self.answer = "ПУСТО"
                    method = self._edit_answer
                    response = "Введите ответ, который заменит ответ '" + self.answer + "':"
                    keyboard = None
            else:
                response = "Некорректные данные для редактирования.\nПродолжаем...\n" + self._find_null()
        else:
            self._request("UPDATE answers SET " + self.group + " = '" + self._txt(message) + "' WHERE id = " + str(self.ind), False, True)
            response = "Ответ добавлен.\n" + self._find_null()

            if self.flag:
                tmp = self._main(None)
                method = tmp[1]
                response += "Следует добавить новые группы\n" + tmp[0]
                keyboard = self.keymode

        return response, method, keyboard

    # поиск записи, в которой нет ответа
    def _find_null(self):
        self._connect()
        groups = self._request("pragma table_info(answers)", True, False)
        groups = groups[2: len(groups)]

        response = "Я знаю ответы на все группы слов. "
        self.flag = True

        for group in groups:
            ind = 1
            group = group[1]
            answers = self._request("SELECT " + group + " FROM answers", True, False)
            for answer in answers:
                if answer[0] is None:
                    old_group = self._request("SELECT column FROM answers WHERE id = " + str(ind), True, False)[0][0]
                    self.flag = False
                    self.group = group
                    self.ind = ind
                    new_group = group

                    # бронирование ячейки для конкретного пользователя, что бы другой не мог редактировать её
                    self._request("UPDATE answers SET " + self.group + " = '*' WHERE id= " + str(ind), False, True)

                    if old_group == "none":
                        old_group = "НЕИЗВЕСТНО"

                    if new_group == "none":
                        new_group = "НЕИЗВЕСТНО"

                    response = "Тема предыдущего сообщения - " + str(old_group).upper() + \
                               "\nТема нового сообщения - " + str(new_group).upper()
                    break
                ind += 1

            if not self.flag:
                break

        return response

    # изменение ответа
    def _edit_answer(self, message):
        keyboard = self.keyback
        method = self._answers
        message = self._txt(message)
        self._connect()
        self._request("UPDATE answers SET " + self.new_message + " = '" + self._txt(message) + "'  WHERE  column = '" + self.old_message + "'", False, True)
        response = "Ответ '" + self.answer + "' изменён на '" + self._txt(message) + "'\nПродолжаем...\n" + self._find_null()
        return response, method, keyboard

    """
    ГРУППЫ
        """
    # инструкция к созданию группы
    def _groups(self, message):
        keyboard = self.keyback
        if message.lower() == "назад":
            tmp = self._main(None)
            method = tmp[1]
            response = "Возвращение в меню выбора.\n" + tmp[0]
            keyboard = self.keymode
        elif message.lower() == "создать группу":
            method = self._create_group
            response = "Придумай нескольлко слов похожих по смыслу, и подумай что их объединяет. " \
                       "На основе своих размышлений придумай и введи название группы:"
        else:
            method = self._groups
            response = "СОЗДАТЬ ГРУППУ - для создания группы."
            keyboard = {
                "inline": True,
                "buttons": [
                    [self.button("Создать группу", "primary")],
                    [self.button("Назад", "negative")]
                ]}

        return response, method, keyboard

    # создание группы
    def _create_group(self, message):
        keyboard = {
            "inline": True,
            "buttons": [
                [self.button("Создать группу", "primary")],
                [self.button("Назад", "negative")]
            ]}
        message = self._punctuation(message.lower())
        if message == "назад":
            tmp = self._main(None)
            method = tmp[1]
            response = "Возвращение в меню выбора.\n" + tmp[0]
            keyboard = self.keymode
        elif len(message.split(" ")) == 1:
            method = self._create_group
            response = "Такая группа уже существует! Введи другое название:"
            self._connect()
            groups = self._request("pragma table_info(words)", True, False)
            groups = self._extraction(groups, 1)
            keyboard = self.keyback

            if message not in groups:
                tmp = self._main(None)
                method = tmp[1]
                self._request("ALTER TABLE words ADD COLUMN '" + message + "' TEXT", False, False)
                self._request("ALTER TABLE answers ADD COLUMN '" + message + "' TEXT", False, False)
                self._request("INSERT INTO answers (column) VALUES ('" + message + "')", False, True)
                response = "Группа " + message.upper() + " добавлена.\nВозвращение в меню выбора.\n" + tmp[0]
                keyboard = self.keymode
        else:
            response = "Введи не менее и не более одного слова!"
            method = self._create_group

        return response, method, keyboard

    """
    ФРАЗЫ
        """
    # добавление фразы
    def _phrases_inp(self, message):
        keyboard = None
        method = self._phrases_out
        response = "Теперь введи, что мне нужно отвечать пользователю на это сообшение:"
        message = self._punctuation(message).lower()
        if message == "назад":
            tmp = self._main(None)
            method = tmp[1]
            response = "Возвращение в меню выбора.\n" + tmp[0]
            keyboard = self.keymode
        else:
            self._connect()
            self.ind = self._request("SELECT id FROM phrases WHERE input = '" + self._punctuation(message.lower()) + "'", True, False)
            if len(self.ind):
                self.ind = self.ind[0][0]
                method = self._edit_phrase_inp
                response = "Введи фразу, которая заменит фразу '" + message.capitalize() + "':"
                self._request("UPDATE phrases SET input = '*' WHERE id = '" + str(self.ind) + "'", False, True)
                self.phrase = message
            else:
                word = None
                if len(message.split(" ")) == 1:
                    word = self._find_group(message.lower())
                    if word:
                        method = self._phrases_inp
                        response = "Это слово уже есть в группе " + word.capitalize() + "! Введи что-нибудь другое:"

                if not word:
                    self._request("INSERT INTO phrases (input, output) VALUES ('" + self._punctuation(message) + "', '*')", False, True)
                    self.ind = len(self._request("SELECT id FROM phrases", True, False))

        return response, method, keyboard

    # добавление ответа на фразу
    def _phrases_out(self, message):
        keyboard = self.keyback
        self._connect()
        self._request("UPDATE phrases SET output = '" + message + "' WHERE id = " + str(self.ind), False, True)
        method = self._phrases_inp
        response = "Фраза-Ответ добавлены" \
                   "\nВведи текст другого сообщения, на которое я должен ответить:"

        return response, method, keyboard

    # редактирование фразы
    def _edit_phrase_inp(self, message):
        self._connect()
        if not len(self._request("SELECT id FROM phrases WHERE input = '" + self._punctuation(message.lower()) + "'", True, False)):
            self.answer = self._request("SELECT output FROM phrases WHERE id = " + str(self.ind), True, False)[0][0]
            method = self.edit_phrase_out
            response = "Фраза '" + self.phrase.capitalize() + "' заменена на фразу '" + message.capitalize() + "'." \
                       "\nТеперь введи ответ, который заменит ответ '" + self.answer + "':"
            word = None
            if len(message.split(" ")) == 1:
                word = self._find_group(message.lower())
                if word:
                    method = self._edit_phrase_inp
                    response = "Это слово уже есть в группе " + word.upper() + "! Введи что-нибудь другое:"

            if not word:
                self._connect()
                self._request("UPDATE phrases SET input = '" + self._punctuation(message.lower()) + "' WHERE id = " + str(self.ind), False, True)
                self.answer = self._request("SELECT output FROM phrases WHERE id = " + str(self.ind), True, False)[0][0]
        else:
            method = self._edit_phrase_inp
            response = "Эта фраза уже есть! Введи другую:"

        return response, method, None

    # редактирование ответа на фразу
    def edit_phrase_out(self, message):
        keyboard = self.keyback
        self._connect()
        self._request("UPDATE phrases SET output = '" + message + "' WHERE id = " + str(self.ind), False, True)
        method = self._phrases_inp
        response = "Ответ '" + self.answer + "' заменён на ответ '" + message.capitalize() + "'." \
                   "\nФраза-Ответ изменены!" \
                   "\nВведи текст сообщения, на которое я должен ответить:"

        return response, method, keyboard

    """
    САМОСТОЯТЕЛЬНЫЕ МЕТОДЫ
        """
    # поиск группы по слову
    def _find_group(self, word):
        self._connect()
        groups = self._request("pragma table_info(words)", True, False)
        groups.pop(0)
        groups = self._extraction(groups, 1)
        group_name = None
        if word == "неизвестно":
            group_name = "none"
        else:
            for group in groups:
                words = self._request("SELECT " + group + " FROM words", True, False)
                words = self._extraction(words, 0)
                if word in words:
                    group_name = group
                    break

        return group_name

    # избавление объектов списка/словаря от скобок и кавычек
    @staticmethod
    def _extraction(lst, ind):
        new = []
        for obj in lst:
            if obj is None:
                break

            new.append(obj[ind])

        return new

    # переводит все буквы после '. ' в верхний регистр
    @staticmethod
    def _txt(text):
        string = ""
        for sentence in text.split(". "):
            string += sentence.capitalize() + ". "
        string = string[0:-2]
        return string

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

    # избавление сообщения от символов, отличных от букв и цифр
    @staticmethod
    def _punctuation(message):
        punctuations = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", ",", ".", "?", "|", "/", ":", ";"]
        for p in punctuations:
            if p in message:
                message = message.replace(p, '')
        return message

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
