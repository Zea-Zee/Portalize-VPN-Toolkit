import requests
import json
import uuid
import urllib3
import os
from datetime import datetime, timedelta, timezone

from random import randint


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def save_json(data, folder="./json"):
    os.makedirs(folder, exist_ok=True)  # Создаём папку, если её нет

    # Определяем индекс файла
    files = [f for f in os.listdir(folder) if f.startswith("res") and f.endswith(".json")]
    indexes = [int(f[3:-5]) for f in files if f[3:-5].isdigit()]
    next_index = max(indexes, default=-1) + 1  # Вычисляем следующий индекс

    file_path = os.path.join(folder, f"res{next_index}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"JSON сохранён: {file_path}")


def add_date(date: datetime, days: int = 0, months: int = 0, years: int = 0) -> datetime:
    year = date.year + years
    month = date.month + months
    if month > 12:
        year += month // 12
        month = month % 12
    new_date = date.replace(year=year, month=month) + timedelta(days=days)
    return new_date


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
            self.headers["Cookie"] = f"3x-ui={self.session_id}"
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
        if response.status_code == 200:
            try:
                # response.
                data = response.json()  # Попробуем разобрать ответ как JSON
                print("Gotten inbounds:", data)
                save_json(data)
                # print("Gotten inbounds:\n", json.dumps(data, indent=4, ensure_ascii=False))
            except ValueError:
                # Выводим текст ответа в случае ошибки
                print("Ошибка при разборе JSON:", response.text)
        else:
            print(f"Ошибка при получении inbound: {response.text}")

    def create_client(
        self,
        email: str,
        limitIp: int = 1,
        totalGB: int = 1,
        expiryTime: datetime = None,
        enable: bool = True,
        flow: str = "xtls-rprx-vision"
        ):

        if expiryTime is None:
            expiryTime = int(datetime.now(timezone.utc).timestamp())
        expiryTime_ms = expiryTime * 1000

        """Создание нового клиента."""
        if not self.session_id:
            print("Выполняем вход")
            self.login()

        url = f'{self.host}/panel/api/inbounds/addClient'

        client_id = str(uuid.uuid4())  # Генерируем случайный UUID
        settings = {
            "clients": [
                {
                    "id": client_id,
                    "flow": flow,
                    "email": email,
                    "limitIp": limitIp,
                    "totalGB": totalGB * 1024 * 1024 * 1024,
                    "expiryTime": expiryTime_ms,
                    "enable": enable,
                    "tgId": email,
                    "subId": "test",
                    "comment": "Generated via API",
                    "reset": 0
                }
            ]
        }

        payload = {
            "id": 2,  # id должен быть как в веб-запросе
            "settings": json.dumps(settings)  # Оборачиваем в json.dumps()
        }

        response = requests.post(url, headers=self.headers, json=payload, verify=False)

        if response.status_code == 200:
            print("Клиент успешно создан:", response.json())
        else:
            print(f"Ошибка при создании клиента: {response.text}")

    def delete_client(self, email: str):
        """Удаление клиента по email."""
        if not self.session_id:
            print("Выполняем вход")
            self.login()

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
            print("Выполняем вход")
            self.login()

        url = f'{self.host}/panel/api/inbounds/clientIps/{email}'
        self.headers["Cookie"] = f"session={self.session_id}"

        response = requests.post(url, headers=self.headers, verify=False)

        if response.status_code == 200:
            print("IP-адреса клиента:", response.json())
        else:
            print(f"Ошибка при получении IP-адресов: {response.text}")


# Пример использования класса
if __name__ == "__main__":
    host = 'http://146.19.84.226:63421/FkBjyBdK1VMog32'
    user = 'Kp9fI2bfj5'
    password = 'npYEcjPr5E'
    api = X3API(host=host, user=user, password=password)

    # api.get_inbounds()

    email = "api_test" + str(randint(0, 100000))
    expiryTime = int(add_date(datetime.now(timezone.utc), years=1).timestamp())
    api.create_client(email=email, expiryTime=expiryTime)

    # # Получение IP-адресов клиента
    # api.get_client_ips(email="newclient@example.com")

    # # Удаление клиента
    # api.delete_client(email="newclient@example.com")
