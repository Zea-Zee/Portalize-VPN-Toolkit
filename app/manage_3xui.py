import requests
import json
import uuid
import urllib3
import os

from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

import asyncio
import aiohttp

from random import randint


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def save_json(data, folder="./json"):
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
    return date + relativedelta(years=years, months=months, days=days)


class X3API:
    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password
        self.session_id = None
        self.headers = {
            "Accept": "application/json"
        }
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def login(self):
        async with self.session.post(
            f'{self.host}/login',
            json={
                "username": self.user,
                "password": self.password
            },
            ssl=False
        ) as response:
            if response.status == 200:
                self.session_id = response.cookies.get("3x-ui")
                if self.session_id:
                    self.headers["Cookie"] = f"3x-ui={self.session_id.value}"
                    print("Успешный вход в систему")
                else:
                    print("Не удалось получить session_id из ответа")
            else:
                print(f"Ошибка при входе: {await response.text()}")

    async def get_inbounds(self):
        if not self.session_id:
            print("Выполняем вход")
            await self.login()

        url = f'{self.host}/panel/api/inbounds/list'
        async with self.session.get(url, headers=self.headers, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                print("Получены inbounds:", data)

                # Парсим JSON-строки в нормальные объекты Python
                for inbound in data.get("obj", []):  # Предполагаем, что данные в "obj"
                    for key in ["settings", "streamSettings", "sniffing", "allocate"]:
                        if key in inbound and isinstance(inbound[key], str):
                            try:
                                inbound[key] = json.loads(inbound[key])
                            except json.JSONDecodeError:
                                print(f"Ошибка парсинга {key} у inbound {inbound.get('tag')}")

                await save_json(data)
            else:
                print(f"Ошибка при получении inbound: {await response.text()}")

    async def create_client(
        self,
        email: str = None,
        tg_id: int = None,
        tg_username: str = None,
        limitIp: int = 1,
        totalGB: int = 200,
        expiryTime: datetime = None,
        enable: bool = True,
        flow: str = "xtls-rprx-vision"
    ):
        """Асинхронное создание нового клиента."""
        # Формируем email из tg_id и tg_username если они предоставлены
        if email is None and tg_id is not None and tg_username is not None:
            email = f"{tg_id}_@{tg_username}"
        
        if email is None:
            print("Ошибка: не предоставлен email или параметры tg_id/tg_username")
            return {"success": False, "error": "No email or tg parameters provided"}

        if expiryTime is None:
            curr_time = datetime.now(timezone.utc)
            expiryTime = int(add_date(curr_time, months=1).timestamp())
        expiryTime_ms = expiryTime * 1000

        if not self.session_id:
            print("Выполняем вход")
            await self.login()

        url = f'{self.host}/panel/api/inbounds/addClient'

        client_id = str(uuid.uuid4())
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

        # TODO: вероятнее всего id нужно брать от из inbound'а
        payload = {
            "id": 2,
            "settings": json.dumps(settings)
        }

        try:
            async with self.session.post(
                url, headers=self.headers, json=payload, ssl=False
            ) as response:
                if response.status == 200:
                    try:
                        # Проверяем content-type ответа
                        content_type = response.headers.get('Content-Type', '')
                        if 'application/json' in content_type:
                            data = await response.json()
                            print("Клиент успешно создан:", data)
                        else:
                            text = await response.text()
                            print("Ответ на создание клиента:", text)
                        
                        # Получаем данные для подключения
                        try:
                            # Формируем URL для подключения
                            # Формат: vless://[id]@[host]:[port]?[params]
                            server_host = self.host.split('//')[1].split('/')[0].split(':')[0]
                            config_url = f"vless://{client_id}@{server_host}:443?encryption=none&security=tls&type=tcp&headerType=none#{email}"
                            
                            return {
                                "success": True, 
                                "client_id": client_id,
                                "email": email,
                                "config": config_url
                            }
                        except Exception as e:
                            print(f"Ошибка формирования конфигурации: {e}")
                            return {"success": True, "error": "Config generation failed"}
                    except Exception as e:
                        print(f"Ошибка при чтении ответа: {e}")
                        # Если ошибка в чтении, но статус 200, считаем успешным
                        return {"success": True, "error": "Response parsing failed"}
                else:
                    try:
                        text = await response.text()
                        print(f"Ошибка при создании клиента: {text}")
                    except Exception as e:
                        print(f"Ошибка при получении ответа: {e}")
                        print(f"Код ответа: {response.status}")
                    return {"success": False, "error": f"HTTP error: {response.status}"}
        except Exception as e:
            print(f"Ошибка при запросе создания клиента: {e}")
            return {"success": False, "error": str(e)}

    async def delete_client(self, email: str):
        if not self.session_id:
            print("Выполняем вход")
            await self.login()

        url = f'{self.host}/panel/api/inbounds/deleteClient'
        self.headers["Cookie"] = f"session={self.session_id}"

        payload = {
            "email": email
        }

        async with self.session.post(url, headers=self.headers, json=payload, ssl=False) as response:
            if response.status == 200:
                print("Клиент успешно удален:", await response.json())
            else:
                print(f"Ошибка при удалении клиента: {await response.text()}")

    async def get_client_ips(self, email: str):
        if not self.session_id:
            print("Выполняем вход")
            await self.login()

        url = f'{self.host}/panel/api/inbounds/clientIps/{email}'
        self.headers["Cookie"] = f"session={self.session_id}"

        async with self.session.post(url, headers=self.headers, ssl=False) as response:
            if response.status == 200:
                print("IP-адреса клиента:", await response.json())
            else:
                print(f"Ошибка при получении IP-адресов: {await response.text()}")


async def create_new_client():
    host = 'http://146.19.84.226:63421/FkBjyBdK1VMog32'
    user = 'Kp9fI2bfj5'
    password = 'npYEcjPr5E'

    async with X3API(host=host, user=user, password=password) as api:
        # email = f"api_test_{randint(0, 100000)}"
        # current_time = datetime.now(timezone.utc)
        # expiry_time = int(add_date(current_time, years=1).timestamp())
        # await api.create_client(email=email, expiryTime=expiry_time)
        # print(f"Клиент с email {email} успешно создан.")
        res = await api.get_inbounds()
        print(res)


if __name__ == "__main__":
    asyncio.run(create_new_client())
