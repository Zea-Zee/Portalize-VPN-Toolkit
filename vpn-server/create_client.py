import os
import datetime
import subprocess
import socket


def new_client(name='DEFAULT', tgid=1, confid=1):
    clients_dir = '/root/clients'

    # Проверка существования папки clients и создание, если ее нет
    if not os.path.exists(clients_dir):
        os.makedirs(clients_dir)
        print(f"Directory '{clients_dir}' created.")
    else:
        print(f"Directory '{clients_dir}' already exists.")

    host = socket.gethostname()
    client_name = f"{name}_{host}_{tgid}_{confid}"
    print(f"Creating config {client_name}")

    try:
        with open('client_name.txt', 'w') as file:
            file.write(client_name)

        script_path = os.path.join(os.getcwd(), 'openvpn-install.sh')
        print(script_path)

        result = subprocess.run(['bash', script_path],
                                check=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"New client error {result.stderr.strip()}")

        print(result)

    except Exception as e:
        raise Exception(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        name = input("Enter name of key: ")
        new_client(name)
        print("Successfully created configs")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
