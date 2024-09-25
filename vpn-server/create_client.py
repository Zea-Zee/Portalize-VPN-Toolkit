import os
import datetime
import subprocess
import socket


name = input("Name: ")
enddate = "2099-12-28"#input("End date: YYYY-MM-DD): ")


def create_configs(name: str, enddate: str):
    host = socket.gethostname()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    client_name_1 = f"{host}_{name}_1_{current_date}_{enddate}"
    client_name_2 = f"{host}_{name}_2_{current_date}_{enddate}"

    print(f"Created names are:")
    print(client_name_1)
    print(client_name_2)

    subprocess.run(['sudo', 'chmod', '+x', './openvpn_install.sh'])

    os.environ['NEW_OPENVPN_CLIENT'] = client_name_1
    subprocess.run(['sudo', './openvpn_install.sh'])

    os.environ['NEW_OPENVPN_CLIENT'] = client_name_2
    subprocess.run(['sudo', './openvpn_install.sh'])


create_configs(name, enddate)

print(f"Successfully created configs")
