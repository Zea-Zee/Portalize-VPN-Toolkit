#!/bin/bash

# Путь к конфигурационному файлу
CONFIG_PATH="/etc/openvpn/client.conf"


install() {
    if ! command -v openvpn &> /dev/null; then
        echo "Обновление пакетов..."
        sudo apt update
        echo "Установка OpenVPN..."
        sudo apt install -y openvpn
    fi

    echo "OpenVPN установлен, переходим к установке конфига"
    setconfig
}

setconfig() {
    read -p "Введите путь к вашему конфигурационному файлу .ovpn: " FILE_PATH
    if [ -f "$FILE_PATH" ]; then
        echo "Копирование конфигурационного файла..."
        sudo cp "$FILE_PATH" "$CONFIG_PATH"
        echo "Конфигурация установлена."
        echo "Чтобы включить vpn вызовите метод turnon"
        echo "Чтобы автоматически при запуске системы включать VPN запустите метод set_on_launch"
    else
        echo "Файл не найден, проверьте путь и попробуйте снова"
    fi
}

turnoff() {
    echo "Отключение OpenVPN..."
    sudo systemctl stop openvpn@client
    echo "OpenVPN отключён."
    echo "Чтобы включить вызовите turnon"
}



turnon() {
    if [[ $(systemctl is-active openvpn@client) == "active" ]]; then
        echo "OpenVPN уже активен. Отключаем..."
        sudo systemctl stop openvpn@client
        echo "OpenVPN отключён."
    fi

    ORIGINAL_IP=$(curl -s ifconfig.me)
    echo "Ваш оригинальный IP-адрес: $ORIGINAL_IP"

    echo "Включение OpenVPN..."
    sudo systemctl start openvpn@client
    if [[ $? -eq 0 ]]; then
        echo "Не удалось включить OpenVPN."
        return
    fi

    if [[ $(systemctl is-active openvpn@client) == "active" ]]; then
        echo "OpenVPN включен."

        # Проверка доступности Google
        echo "Проверка доступности Google.com"
        if ping -c 4 google.com > /dev/null; then
            echo -e "\e[32m✓ Google доступен.\e[0m"  # Зеленая галочка
        else
            echo -e "\e[31m✗ Google недоступен.\e[0m"  # Красный крестик
        fi

        # Получение текущего IP-адреса
        CURRENT_IP=$(curl -s ifconfig.me)
        echo "Ваш текущий IP-адрес: $CURRENT_IP"

        # Извлечение ожидаемого IP-адреса из конфигурационного файла
        EXPECTED_IP=$(grep -oP '(?<=remote\s)(\S+)' "$CONFIG_PATH" | awk '{print $1}' | head -n 1)

        # Сравнение IP-адресов
        if [[ "$CURRENT_IP" == "$EXPECTED_IP" ]]; then
            echo -e "\e[32m✓ IP совпадает с VPN IP, вы в безопасности: $EXPECTED_IP\e[0m"
        else
            echo -e "\e[31m✗ IP не совпадает с VPN IP, что-то пошло не так: $EXPECTED_IP (текущий: $CURRENT_IP)\e[0m"
        fi
    else
        echo "OpenVPN не удалось активировать."
    fi
}




set_on_launch() {
    echo "Добавление OpenVPN в автозагрузку..."
    sudo systemctl enable openvpn@client
    echo "OpenVPN добавлен в автозагрузку."
    echo "Чтобы убрать из загрузки вызовите reset_on_launch"
}

reset_on_launch() {
    echo "Удаление OpenVPN из автозагрузки..."
    sudo systemctl disable openvpn@client
    echo "OpenVPN удалён из автозагрузки."
}

help() {
    echo "Доступные команды:"
    echo "  install           Установить OpenVPN"
    echo "  setconfig         Настроить конфигурацию OpenVPN"
    echo "  turnoff           Отключить OpenVPN"
    echo "  turnon            Включить OpenVPN"
    echo "  set_on_launch     Добавить OpenVPN в автозагрузку"
    echo "  reset_on_launch   Удалить OpenVPN из автозагрузки"
    echo "  help              Показать все команды"
    echo "Напишите ./manage_openvpn.sh название_команды"
}

# Оптимальный метод вызова функций
case "$1" in
    install) install ;;
    setconfig) setconfig ;;
    turnoff) turnoff ;;
    turnon) turnon ;;
    set_on_launch) set_on_launch ;;
    reset_on_launch) reset_on_launch ;;
    help) help ;;
    h) help ;;
    *) help ;;
esac
