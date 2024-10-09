import re
import subprocess
import json
import os


def filter_client_name(name: str) -> str:
    filtered_name = re.sub(r'[^0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ]', '', name)
    if len(filtered_name) < 3 or not filtered_name or filtered_name is None:
        raise Exception(f"Too short name: {filtered_name}")
    return filtered_name


def load_clients() -> set:
    if os.path.exists('clients.json'):
        try:
            with open('clients.json', 'r') as f:
                clients = json.load(f)
                return set(clients.get('clients', []))
        except Exception as e:
            print(f"Error loading clients: {e}")
    return set()


def save_clients(clients: set) -> None:
    try:
        with open('clients.json', 'w') as f:
            json.dump({'clients': list(clients)}, f)
    except Exception as e:
        print(f"Error saving clients: {e}")


def create_client(client_name=None):
    clients = load_clients()
    if not client_name:
        client_name = input("Enter a name for the client: ")
    filtered_name = filter_client_name(client_name)

    if filtered_name in clients:
        e = f"Client name '{filtered_name}' already exists. Please choose a different name."
        raise Exception(e)

    try:
        with open('client_name.txt', 'w') as f:
            f.write(filtered_name)
        subprocess.run(['bash', 'create_client.sh'], check=True)
        # print("create_client.sh has been executed.")
        clients.add(filtered_name)
        save_clients(clients)
        # print(f"Filtered name '{filtered_name}' written to client_name.txt.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing create_client.sh: {e}")
    except Exception as e:
        print(f"create_client error occurred: {e} name: {filtered_name}")


def remove_client(name=None):
    if not name:
        name = input("Enter the name of the client to remove: ")
    clients = load_clients()
    if name not in clients:
        e = f"Client '{name}' does not exist."
        raise Exception(e)
    filtered_name = filter_client_name(name)

    try:
        with open('removal_client_name.txt', 'w') as f:
            f.write(filtered_name)
        subprocess.run(['bash', 'remove_openvpn.sh'], check=True)
        # print("remove_openvpn.sh has been executed.")
        clients.remove(filtered_name)
        save_clients(clients)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing remove_openvpn.sh: {e}")
    except Exception as e:
        print(f"remove_client error occurred: {e} name: {filtered_name}")


def install_openvpn():
    try:
        subprocess.run(['bash', 'install_openvpn.sh'], check=True)
        print("install_openvpn.sh has been executed.")
        clients = set()
        clients.add('TEST-CLIENT')
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing install_openvpn.sh: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def remove_openvpn():
    try:
        subprocess.run(['bash', 'remove_openvpn.sh'], check=True)
        print("remove_openvpn.sh has been executed.")
        save_clients(set())
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing remove_openvpn.sh: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    option = input(
        "Choose option:\n1 - Create client\n2 - Remove client\n3 - Install openvpn\n4 - Remove openvpn\nOption: ")

    if option == '1':
        create_client()
    elif option == '2':
        remove_client()
    elif option == '3':
        install_openvpn()
    elif option == '4':
        remove_openvpn()
    else:
        print("Invalid option selected.")


if __name__ == "__main__":
    main()

