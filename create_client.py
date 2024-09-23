import os
import datetime
import subprocess


name = "test"#input("Name: ")
specified_date = "2024_10_23"#input("End date: YYYY-MM-DD): ")
host = "MEL_RIG_4"
current_date = datetime.datetime.now().strftime("%Y-%m-%d")

client_name_1 = f"{host}_{name}_1_{current_date}_{specified_date}"
client_name_2 = f"{host}_{name}_2_{current_date}_{specified_date}"

print(f"Created names are:")
print(client_name_1)
print(client_name_2)


def run_openvpn_script(client_name):
    os.environ['NEW_OPENVPN_CLIENT'] = client_name
    subprocess.run(['./install.sh'])
exit()
run_openvpn_script(client_name_1)
run_openvpn_script(client_name_2)
