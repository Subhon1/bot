import json
from datetime import datetime
import urllib.request
import vk_api
import random
import sqlite3


token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество


class Statistic:
    def __init__(self, userID):
        self.userID = userID

    def _different(self, message):
        userMes = 365429965
        userAns = 244304641
        lstUsers = [userMes, userAns]
        MesAns = dict()
        FwdMes = dict()
        indMes = 0
        indBlockMes = 0
        indBlockFwd = 0
        messages, users = self._open(lstUsers)

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

        # ___ONE___
        def one_method(inp, lst):
            answer = list()
            for block in lst:
                if lst[block]["mes"]["text"] == inp:
                    answer.append(lst[block]["ans"]["text"])

            if len(answer) > 0:
                rnd = random.randint(0, len(answer) - 1)
                answer = answer[rnd]

            return answer

        # ___TWO___
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
                rnd = random.randint(0, len(answer)-1)
                answer = answer[rnd]

            return answer

        while True:
            inp = input("-> ")
            length = len(inp.split(' '))
            answer = ''
            for snp in range(length):
                answer = one_method(inp, FwdMes)
                print("    ONE")
                if not answer:
                    answer = one_method(inp, MesAns)
                    print("    TWO")
                    if not answer:
                        answer = two_method(inp, FwdMes)
                        print("    THREE")
                        if not answer:
                            answer = two_method(inp, MesAns)
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
                for word in inp.split(' '):
                    lst.append(word)
                lst = lst[1:]

                inp = ''
                for elm in lst:
                    inp += elm + ' '
                inp = inp[:-1]

            if not answer:
                print("    RANDOM")
                print(MesAns[random.randint(0, len(MesAns)-1)]['ans']['text'])
            else:
                print(answer)


        return 'response', None, None

    @staticmethod
    def _punctuation(message):
        punctuations = ["!", "@", "#", "$", "%", "^", "&", "(", ")", "-", "+", ",", ".", "?", "|", "/", ":", ";", "\n"]
        for p in punctuations:
            if p in message:
                message = message.replace(p, '')
        return message

    @staticmethod
    def _open(lstUsers):
        path = 'data\\chats\\Nastya.json'
        with open(path, 'r', encoding='utf-8') as f:  # открыли файл с данными
            dialog = json.load(f)

        messages = dict()
        num = 0
        for i in range(len(dialog)):
            #  фильтр
            if not dialog[i]['body']:  # без пустых сообщений
                continue
            if "fwd_messages" in dialog[i]:
                if len(dialog[i]['fwd_messages']) > 1:  # без  пересланных кусков сообщений
                    continue

                if dialog[i]['fwd_messages'][0]['user_id'] not in lstUsers:  # без пересланных чужих сообщений
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

        users = dict()
        for i in messages:
            if messages[i]['id'] in users:
                users[messages[i]['id']]['count'] += 1
                users[messages[i]['id']]['messages'].append(messages[i]['text'])
            else:
                user = vk.method("users.get", {"user_ids": int(messages[i]['id'])})
                first_name = user[0]['first_name']
                last_name = user[0]['last_name']
                users[messages[i]['id']] = {'count': 1, 'messages': [messages[i]['text']], 'name': first_name + " " + last_name}

       # for i in messages:
           # print(messages[i]['fwd'])

        return messages, users


cls = Statistic("lol")
met = cls._different("kek")
