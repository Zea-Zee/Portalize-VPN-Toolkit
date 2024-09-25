import os
import datetime
import subprocess
import socket


def new_client(name='DEFAULT', id=1):
    host = socket.gethostname()

    client_name = f"{name}_{host}_{id}"
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
        name = input()
        new_client(name)
        print("Successfully created configs")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
