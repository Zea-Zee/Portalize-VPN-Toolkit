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

    client_common_path = '/etc/openvpn/server/client-common.txt'
    ca_cert_path = '/etc/openvpn/server/easy-rsa/pki/ca.crt'
    client_cert_path = f'/etc/openvpn/server/easy-rsa/pki/issued/{client_name}.crt'
    client_key_path = f'/etc/openvpn/server/easy-rsa/pki/private/{client_name}.key'
    tls_crypt_path = '/etc/openvpn/server/tc.key'

    # Путь для сохранения файла клиента
    output_file = os.path.expanduser(f'~/{client_name}.ovpn')

    try:
        # Чтение и запись в итоговый .ovpn файл
        with open(output_file, 'w') as ovpn_file:
            # client-common.txt
            with open(client_common_path, 'r') as f:
                ovpn_file.write(f.read())

            # ca.crt
            ovpn_file.write("\n<ca>\n")
            with open(ca_cert_path, 'r') as f:
                ovpn_file.write(f.read())
            ovpn_file.write("</ca>\n")

            # client cert
            ovpn_file.write("<cert>\n")
            with open(client_cert_path, 'r') as f:
                inside_cert = False
                for line in f:
                    if 'BEGIN CERTIFICATE' in line:
                        inside_cert = True
                    if inside_cert:
                        ovpn_file.write(line)
            ovpn_file.write("</cert>\n")

            # client key
            ovpn_file.write("<key>\n")
            with open(client_key_path, 'r') as f:
                ovpn_file.write(f.read())
            ovpn_file.write("</key>\n")

            # tls-crypt
            ovpn_file.write("<tls-crypt>\n")
            with open(tls_crypt_path, 'r') as f:
                inside_tls_crypt = False
                for line in f:
                    if 'BEGIN OpenVPN Static key' in line:
                        inside_tls_crypt = True
                    if inside_tls_crypt:
                        ovpn_file.write(line)
            ovpn_file.write("</tls-crypt>\n")

        print(f"Файл конфигурации для клиента {client_name} создан: {output_file}")

    except Exception as e:
        print(f"Ошибка при создании файла конфигурации: {e}")



new_client(name, id)

print(f"Successfully created configs")
