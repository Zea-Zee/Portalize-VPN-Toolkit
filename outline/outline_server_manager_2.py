import requests
import json
import argparse
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Отключение предупреждений о небезопасных запросах
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def load_config(config_path="outline_config.json"):
    """
    Загружает конфиг из файла.
    :param config_path: Путь к файлу конфига.
    :return: Словарь с конфигом.
    """
    try:
        with open(config_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Конфиг-файл {config_path} не найден. Введите данные вручную.")
        api_url = input("Введите apiUrl: ")
        cert_sha256 = input("Введите certSha256: ")
        return {"apiUrl": api_url, "certSha256": cert_sha256}
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла {config_path}. Проверьте формат JSON.")
        return None

def save_config(config, config_path="outline_config.json"):
    """
    Сохраняет конфиг в файл.
    :param config: Словарь с конфигом.
    :param config_path: Путь к файлу конфига.
    """
    with open(config_path, "w") as file:
        json.dump(config, file, indent=4)

def create_access_key(api_url, cert_sha256, name):
    """
    Создает новый ключ доступа для Outline VPN с указанным именем.
    :param api_url: API URL из конфига Outline.
    :param cert_sha256: Сертификат SHA256 для аутентификации.
    :param name: Имя ключа.
    :return: Созданный ключ.
    """
    headers = {"Access-Token": cert_sha256, "Content-Type": "application/json"}
    endpoint = f"{api_url}/access-keys"

    response = requests.post(endpoint, headers=headers, verify=False)
    if response.status_code == 201:
        key_data = response.json()
        key_id = key_data["id"]
        name_endpoint = f"{api_url}/access-keys/{key_id}/name"
        requests.put(name_endpoint, headers=headers, json={"name": name}, verify=False)
        return key_data["accessUrl"]
    else:
        raise Exception(f"Ошибка при создании ключа: {response.status_code}\n{response.text}")

def delete_access_key(api_url, cert_sha256, key_id):
    """
    Удаляет ключ доступа Outline VPN по ID.
    :param api_url: API URL из конфига Outline.
    :param cert_sha256: Сертификат SHA256 для аутентификации.
    :param key_id: ID ключа для удаления.
    """
    headers = {"Access-Token": cert_sha256}
    endpoint = f"{api_url}/access-keys/{key_id}"
    response = requests.delete(endpoint, headers=headers, verify=False)
    if response.status_code != 204:
        raise Exception(f"Ошибка при удалении ключа: {response.status_code}\n{response.text}")

def list_access_keys(api_url, cert_sha256):
    """
    Получает список всех ключей доступа.
    :param api_url: API URL из конфига Outline.
    :param cert_sha256: Сертификат SHA256 для аутентификации.
    :return: Список ключей.
    """
    headers = {"Access-Token": cert_sha256}
    endpoint = f"{api_url}/access-keys"
    response = requests.get(endpoint, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()["accessKeys"]
    else:
        raise Exception(f"Ошибка при получении списка ключей: {response.status_code}\n{response.text}")

def show_statistics(keys):
    """
    Показывает статистику по ключам.
    :param keys: Список ключей.
    """
    print("Статистика ключей:")
    for key in keys:
        name = key.get("name", "Без имени")
        data_limit = key.get("dataLimit", {}).get("bytes", "Нет данных")
        print(f"Ключ: {name}, Потрачено трафика: {data_limit} байт")
        
def save_keys_to_file(keys, filename="keys.txt"):
    """
    Сохраняет информацию о ключах в файл.
    :param keys: Список ключей.
    :param filename: Имя файла для сохранения.
    """
    with open(filename, "w") as file:
        for key in keys:
            # name = key.get("name", "Без имени")
            key_url = key.get("accessUrl", "Нет URL")
            # data_limit = key.get("dataLimit", {}).get("bytes", "Нет данных")
            file.write(f"{key_url}\n")
    print(f"Информация о ключах сохранена в {filename}.")

def main():
    parser = argparse.ArgumentParser(description="Управление ключами Outline VPN.")
    parser.add_argument("--config", help="JSON-конфиг с apiUrl и certSha256.")
    parser.add_argument("--create", help="Создать ключ с указанным именем.")
    parser.add_argument("--create-n", type=int, help="Создать N ключей с автоименем key_k.")
    parser.add_argument("--ensure-n", type=int, help="Досоздать ключи до N.")
    parser.add_argument("--delete", help="Удалить ключ с указанным именем.")
    parser.add_argument("-delete-all", action="store_true", help="Удалить все ключи.")
    parser.add_argument("--replace", help="Заменить ключ с указанным именем.")
    parser.add_argument("-stats", action="store_true", help="Показать статистику по ключам.")
    parser.add_argument("-save_keys", action="store_true", help="Сохранить ключи в файл keys.txt")
    args = parser.parse_args()

    # Загрузка конфига
    config = None
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError:
            print("Ошибка: Неверный формат JSON-конфига.")
            return
    else:
        config = load_config()

    if not config:
        print("Ошибка: Конфиг отсутствует. Программа завершена.")
        return

    api_url = config.get("apiUrl")
    cert_sha256 = config.get("certSha256")

    if args.create:
        key_url = create_access_key(api_url, cert_sha256, args.create)
        print(f"Ключ с именем {args.create} создан. URL доступа: {key_url}")

    if args.create_n:
        for i in range(1, args.create_n + 1):
            key_name = f"key_{i}"
            key_url = create_access_key(api_url, cert_sha256, key_name)
            print(f"Ключ {key_name} создан. URL доступа: {key_url}")

    if args.ensure_n:
        keys = list_access_keys(api_url, cert_sha256)
        current_keys = len(keys)
        if current_keys < args.ensure_n:
            for i in range(current_keys, args.ensure_n):
                key_name = f"key_{i + 1}"
                key_url = create_access_key(api_url, cert_sha256, key_name)
                print(f"Ключ {key_name} создан. URL доступа: {key_url}")

    if args.delete:
        keys = list_access_keys(api_url, cert_sha256)
        for key in keys:
            if key["name"] == args.delete:
                delete_access_key(api_url, cert_sha256, key["id"])
                print(f"Ключ {args.delete} удалён.")
                break

    if args.delete_all:
        keys = list_access_keys(api_url, cert_sha256)
        for key in keys:
            delete_access_key(api_url, cert_sha256, key["id"])
        print("Все ключи удалены.")

    if args.replace:
        keys = list_access_keys(api_url, cert_sha256)
        for key in keys:
            if key["name"] == args.replace:
                delete_access_key(api_url, cert_sha256, key["id"])
                key_url = create_access_key(api_url, cert_sha256, args.replace)
                print(f"Ключ {args.replace} заменён. Новый URL доступа: {key_url}")
                break

    if args.stats:
        keys = list_access_keys(api_url, cert_sha256)
        show_statistics(keys)
        
    if args.save_keys:
        keys = list_access_keys(api_url, cert_sha256)
        save_keys_to_file(keys)

if __name__ == "__main__":
    main()
