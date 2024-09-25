import os
import datetime
import subprocess
import socket


name = input("Name: ")
id = 1
enddate = "2099-12-28"#input("End date: YYYY-MM-DD): ")


def new_client(name, id):
    host = socket.gethostname()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    client_name = f"{name}_{host}_{current_date}_{enddate}_{id}"
    print(f"Creating config {client_name}")

    file = open('client_name.txt', 'w')
    file.write(client_name + '\n')

    subprocess.run(['sudo', 'chmod', '+x', './openvpn_install.sh'])

    subprocess.run(['sudo', './openvpn_install.sh'])


new_client(name, id)

print(f"Successfully created configs")
