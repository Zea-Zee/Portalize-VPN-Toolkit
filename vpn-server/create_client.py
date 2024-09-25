import os
import datetime
import subprocess
import socket


def new_client(name='DEFAULT', id=1, enddate='2099-12-28'):
    host = socket.gethostname()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    client_name = f"{name}_{host}_{current_date}_{enddate}_{id}"
    print(f"Creating config {client_name}")

    try:
        with open('client_name.txt', 'w') as file:
            file.write(client_name)

        script_path = os.path.join(os.getcwd(), 'openvpn-install.sh')
        print(script_path)

        result = subprocess.run(
            ['sudo', 'chmod', '+x', script_path], check=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Failed to change permissions for the script.")

        result = subprocess.run(['bash', script_path],
                                check=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to execute the script. Error: {
                            result.stderr.strip()}")

    except Exception as e:
        raise Exception(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        new_client()
        print("Successfully created configs")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
