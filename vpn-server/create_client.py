import os
import datetime
import subprocess
import json


name = #input("Name: ")
enddate = "noenddate"#input("End date: YYYY-MM-DD): ")


def create_configs(name: str, enddate: str):
    with open('config.json', 'r') as file:
        data = json.load(file)
        host = data.get('hostname')
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    client_name_1 = f"{host}_{name}_1_{current_date}_{enddate}"
    client_name_2 = f"{host}_{name}_2_{current_date}_{enddate}"

    print(f"Created names are:")
    print(client_name_1)
    print(client_name_2)

    os.environ['NEW_OPENVPN_CLIENT'] = client_name_1
    subprocess.run(['./install.sh'])

    os.environ['NEW_OPENVPN_CLIENT'] = client_name_2
    subprocess.run(['./install.sh'])


create_configs(name, enddate)

print(f"Successfully created configs")
