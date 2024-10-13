import requests
import json
import uuid
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class X3API:
    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password
        self.session_id = None
        self.headers = {
            "Accept": "application/json"
        }

    def login(self):
        response = requests.post(
            f'{self.host}/login',
            json={
                "username": self.user,
                "password": self.password
            },
            verify=False)

        if response.status_code == 200:
            # print(response.json())
            print(response.cookies.get("session"))
            print(response.cookies.get("3x-ui"))
            self.session_id = response.cookies.get("3x-ui")
            # print(response.cookies)
            # print(self.session_id)
            self.headers["Cookie"] = f"session={self.session_id}"
            print("Успешный вход в систему")
        else:
            print(f"Ошибка при входе: {response.text}")

    def get_inbounds(self):
        if not self.session_id:
            print("Выполняем вход")
            self.login()

        url = f'{self.host}/panel/api/inbounds/list'
        # print(self.headers)
        response = requests.get(url, headers=self.headers, verify=False)
        print(response.headers)
        return
        if response.status_code == 200:
            try:
                # response.
                data = response.json()  # Попробуем разобрать ответ как JSON
                print("Gotten inbounds:", data)
            except ValueError:
                print("Ошибка при разборе JSON:", response.text)  # Выводим текст ответа в случае ошибки
        else:
            print(f"Ошибка при получении inbound: {response.text}")

    def create_client(self, email: str):
        """Создание нового клиента."""
        if not self.session_id:
            print("Сначала выполните вход в систему")
            return

        url = f'{self.host}/panel/api/inbounds/addClient'

        client_id = str(uuid.uuid4())
        payload = {
            "id": 1,
            "settings": json.dumps({
                "clients": [
                    {
                        "id": client_id,
                        "alterId": 90,
                        "email": email,
                        "limitIp": 3,
                        "totalGB": 0,
                        "expiryTime": 0,
                        "enable": True,
                        "tgId": email,
                        "subId": ""
                    }
                ]
            })
        }

        response = requests.post(
            url, headers=self.headers, json=payload, verify=False)

        if response.status_code == 200:
            print("Клиент успешно создан:", response.json())
        else:
            print(f"Ошибка при создании клиента: {response.text}")

    def delete_client(self, email: str):
        """Удаление клиента по email."""
        if not self.session_id:
            print("Сначала выполните вход в систему")
            return

        url = f'{self.host}/panel/api/inbounds/deleteClient'
        self.headers["Cookie"] = f"session={self.session_id}"

        payload = {
            "email": email
        }

        response = requests.post(
            url, headers=self.headers, json=payload, verify=False)

        if response.status_code == 200:
            print("Клиент успешно удален:", response.json())
        else:
            print(f"Ошибка при удалении клиента: {response.text}")

    def get_client_ips(self, email: str):
        """Получение IP-адресов клиента по email."""
        if not self.session_id:
            print("Сначала выполните вход в систему")
            return

        url = f'{self.host}/panel/api/inbounds/clientIps/{email}'
        self.headers["Cookie"] = f"session={self.session_id}"

        response = requests.post(url, headers=self.headers, verify=False)

        if response.status_code == 200:
            print("IP-адреса клиента:", response.json())
        else:
            print(f"Ошибка при получении IP-адресов: {response.text}")


# Пример использования класса
if __name__ == "__main__":
    api = X3API(host="http://89.36.161.85:51721/vWF2dlUjXSS9iDg", user="", password="")
    
    # api.get_inbounds()
    # api.create_client(email="newclient@example.com")

    # # Получение IP-адресов клиента
    # api.get_client_ips(email="newclient@example.com")

    # # Удаление клиента
    # api.delete_client(email="newclient@example.com")
