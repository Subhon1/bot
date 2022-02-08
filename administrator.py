import sqlite3
import vk_api

token = "c034acdbc6e603556e8202e0d0138a7bd965e3458f98dfd057d7d93813dda5520fe2c4c829a2cd7bef40e"  # API-ключ
vk = vk_api.VkApi(token=token)  # авторизуемся как сообщество

class Administrator:

    def __init__(self, userID):
        self.userID = userID
        self.commands = {"книга": self._book}
        roles = {"creator": 1, "administrator": 2, "editor": 3, "moderator": 4}
        self.accessAdmin = list()
        response = vk.method("groups.getMembers", {"group_id": 164076806, "filter": "managers"})
        for user in response["items"]:
            if roles[user["role"]] <= 2:
                self.accessAdmin.append(user["id"])

        print("users", self.accessAdmin)

    def _main(self, message):
        flag = False
        for user in self.accessAdmin:
            if self.userID == user:
                flag = True

        if flag:
            method = self._distributor
            response = "Команда:"
        else:
            method = None
            response = "Недоступно"

        return response, method, None

    def _distributor(self, message):
        message = message.lower()
        if message in self.commands:
            response = self.commands[message]()
            method = self._distributor
        else:
            response = "Отказ"
            method = self._distributor

        return response, method, None

    def _book(self):
        self._connect()
        usersIDS = self._request("SELECT id FROM book ORDER BY id", True, False)
        statements = self._request("SELECT statement FROM book ORDER BY id", True, False)

        statementsLst = ""
        for i in range(len(statements)):
            statementsLst += "vk.com/id" + str(usersIDS[i][0]) + " - " + statements[i][0] + "\n"

        return statementsLst

    # ---------------------------------------------------------------------------------
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
