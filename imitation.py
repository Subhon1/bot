import json
from datetime import datetime
import urllib.request
import vk_api
import random
import os


token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество


class Imitation:
    def __init__(self, userID):
        self.userID = userID
        self.MesAns = dict()
        self.FwdMes = dict()
        self.users = dict()
        self.dialog = list()

    def _main(self, message, items):
        response = "Отправте мне файл переписки в формате .json. \nО том, как этот файл получить, читайте в статье 'Nostalgia'."
        method = self._odd_man_out
        return response, method, None

    def _analyze(self, messages, userMes, userAns):
        MesAns = dict()
        FwdMes = dict()

        indMes = 0
        indBlockMes = 0
        indBlockFwd = 0

        for indNow in messages:
            if indNow == 0:
                continue
            else:
                if messages[indMes]['id'] == userMes:
                    if messages[indNow]['id'] == userAns:
                        MesAns[indBlockMes] = {'mes': {'date': messages[indMes]['date'],
                                                       'text': self._punctuation(messages[indMes]['text']).lower()},
                                               'ans': {'date': messages[indNow]['date'],
                                                       'text': messages[indNow]['text']}}
                        indBlockMes += 1

                elif len(messages[indMes]['fwd']) > 0:
                    FwdMes[indBlockFwd] = {'mes': {'date': None,
                                                   'text': self._punctuation(messages[indMes]['fwd']).lower()},
                                           'ans': {'date': messages[indMes]['date'],
                                                   'text': messages[indMes]['text']}}
                    indBlockFwd += 1

            indMes += 1

        self.MesAns = MesAns
        self.FwdMes = FwdMes

    def _find(self, message, items):
        method = self._find
        message = self._punctuation(message).lower()
        length = len(message.split(' '))
        answer = ''
        for snp in range(length):
            answer = self.one_method(message, self.FwdMes)
            print("    ONE")
            if not answer:
                answer = self.one_method(message, self.MesAns)
                print("    TWO")
                if not answer:
                    answer = self.two_method(message, self.FwdMes)
                    print("    THREE")
                    if not answer:
                        answer = self.two_method(message, self.MesAns)
                        print("    FOUR")
                        if answer:
                            break
                    else:
                        break
                else:
                    break
            else:
                break

            lst = list()
            for word in message.split(' '):
                lst.append(word)
            lst = lst[1:]

            message = ''
            for elm in lst:
                message += elm + ' '
            message = message[:-1]

        if not answer:
            print("    RANDOM")
            answer = self.MesAns[random.randint(0, len(self.MesAns) - 1)]['ans']['text']

        response = answer

        return response, method, None

    # ___One_Method___
    @staticmethod
    def one_method(inp, lst):
        answer = list()
        for block in lst:
            if lst[block]["mes"]["text"] == inp:
                answer.append(lst[block]["ans"]["text"])

        if len(answer) > 0:
            rnd = random.randint(0, len(answer) - 1)
            answer = answer[rnd]

        return answer

    # ___Two_Method___
    @staticmethod
    def two_method(inp, lst):
        answer = list()
        for block in lst:
            txtMes = lst[block]["mes"]["text"]

            if len(inp.split(" ")) < len(txtMes):
                lstInp = list()

                for word in inp.split(" "):
                    lstInp.append(word)
                lstMes = list()
                for word in txtMes.split(" "):
                    lstMes.append(word)

                length = (len(lstMes) - len(lstInp)) + 1
                for snp in range(length):
                    if lstInp == lstMes[snp: snp + len(lstInp)]:
                        answer.append(lst[block]['ans']['text'])
                        break

        if len(answer) > 0:
            rnd = random.randint(0, len(answer) - 1)
            answer = answer[rnd]

        return answer

    @staticmethod
    def _punctuation(message):
        punctuations = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", ",", ".", "?", "|", "/", ":", ";", "\n"]
        for p in punctuations:
            if p in message:
                message = message.replace(p, '')
        return message

    def _open(self):
        flag = False
        messages = dict()
        num = 0
        dialog = self.dialog
        try:
            for i in range(len(dialog)):
                #  фильтр
                if not dialog[i]['body']:  # без пустых сообщений
                    continue
                if "fwd_messages" in dialog[i]:
                    if len(dialog[i]['fwd_messages']) > 1:  # без  пересланных кусков сообщений
                        continue
    
                    if dialog[i]['fwd_messages'][0]['user_id'] not in self.users:  # без пересланных чужих сообщений
                        continue
    
                    if dialog[i]['from_id'] == dialog[i]['fwd_messages'][0]['user_id']:  # без пересланных своих сообщений
                        continue
                #  фильтр\
    
                fwd = ''
                if "fwd_messages" in dialog[i]:
                    fwd = dialog[i]['fwd_messages'][0]['body']
    
                messages[num] = {'id': dialog[i]['from_id'],
                                 'date': datetime.fromtimestamp(int(dialog[i]['date'])).strftime('%Y-%m-%d %H:%M:%S'),
                                 'text': dialog[i]['body'],
                                 'fwd': fwd}
                num += 1
        except:
            flag = True

        return messages, flag

    def _odd_man_out(self, message, items):
        try:
            path = 'data\\chats\\' + items['name']
            urllib.request.urlretrieve(items['URL'], path)
            with open(path, 'r', encoding='utf-8') as f:  # открытие файла с данными
                self.dialog = json.load(f)

            # path = os.path.join(os.path.abspath(os.path.dirname(__file__)), path)
            # os.remove(path)

            sUsers = set()  # множество ИД пользователей
            for i in range(len(self.dialog)):
                sUsers.add(self.dialog[i]['from_id'])

            if len(sUsers) == 2:
                method = self._choice
                response = 'Кого мне следует имитировать?\n'
                users = dict()
                btns = list()
                for idu in sUsers:
                    user = vk.method("users.get", {"user_ids": idu})
                    users[user[0]['first_name'] + " " + user[0]['last_name'][:1] + ". " + str(idu)] = idu
                self.users = users

                for user in users:
                    btns.append(self.button(user, "positive"))
                    response += '-' + user + '\n'

                keyboard = {
                    "one_time": True,
                    "buttons": [
                        [self.button("Стоп", "negative")],
                        btns,

                    ]}
            else:
                keyboard = {
                    "one_time": True,
                    "buttons": [
                        [self.button("Стоп", "negative")],

                    ]}
                method = self._odd_man_out
                response = 'Собеседников должно быть 2-е. А в этом чате их - ' + str(len(sUsers)) + '\nОтправте другой файл:'
        except KeyError:
            response = "Нужно отправить мне файл в формате .json"
            method = self._odd_man_out
            keyboard = None
        except:
            response = "Некорректный файл! Отправте другой:"
            method = self._odd_man_out
            keyboard = None

        return response, method, keyboard

    def _choice(self, message, items):
        users = self.users
        keyboard = None
        if message in users:
            method = self._find
            response = 'Я  - система имитации - ' + message.split(" ")[:1][0] + '. Можете со мной общаться:'
            userAns = users[message]
            userMes = 0
            for user in users:
                if user != message:
                    userMes = users[user]
                    break

            messages, flag = self._open()
            if flag:
                response = "Некорректный файл! Отправте другой:"
                method = self._odd_man_out
                
            self._analyze(messages, userMes, userAns)
        else:
            method = self._choice
            response = 'Чёт не правильно. Выберите пользователя из списка:\n'
            btns = list()
            for user in users:
                btns.append(self.button(user, "positive"))
                response += '-' + user + '\n'

            keyboard = {
                "one_time": True,
                "buttons": [
                    [self.button("Стоп", "negative")],
                    btns,

                ]}

        return response, method, keyboard

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
