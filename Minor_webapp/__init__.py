from flask import Flask, render_template, app, request
import paho.mqtt.client as mqtt
from threading import Thread
from datetime import date
import datetime
import os

msg = "qwerty"
"""
# корректировка базы пользователей в таблице exel
import pandas as pd

df = pd.DataFrame({'Имя': ['Никулин ВС', 'Сартасова НЕ', 'Тохтамир НП'],
                   'Местоположение': ['55.669732, 37.478907', '54.669732, 37.478907', '56.669732, 37.478907'],
                   'Пароль': [111, 222, 333]})
df.to_excel('./users.xlsx', sheet_name='Пользователи', index=False)
"""


# настройка подписки на топик MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code : " + str(rc))
    client.subscribe("minor/0001/#")


# настройка вывода сообщений MQTT
def on_message(client, userdata, msg):
    print(msg.topic, msg.payload)
    m = msg.payload
    st = str(m)
    st = st.split('\'')
    message_processing(st[1])


# статус запуска сайта
siteLaunched = False


# Отправить письмо на эл.почту
def goMessege(str):
    import smtplib  # Импортируем библиотеку по работе с SMTP

    # Добавляем необходимые подклассы - MIME-типы
    from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
    from email.mime.text import MIMEText  # Текст/HTML
    from email.mime.image import MIMEImage  # Изображения

    addr_from = "IoT_Helper@yahoo.com"  # Адресат
    addr_to = "642[...]64@mail.com"  # Получатель
    password = "IoTxrtr5[...]5GlQfg"  # Пароль

    msg = MIMEMultipart()  # Создаем сообщение
    msg['From'] = addr_from  # Адресат
    msg['To'] = addr_to  # Получатель
    msg['Subject'] = 'Уведомление от IoT Helper'  # Тема сообщения

    body = msg
    msg.attach(MIMEText(body, 'plain'))  # Добавляем в сообщение текст

    server = smtplib.SMTP('smtp-server', 587)  # Создаем объект SMTP
    server.set_debuglevel(True)  # Включаем режим отладки - если отчет не нужен, строку можно закомментировать
    server.starttls()  # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)  # Получаем доступ
    server.send_message(msg)  # Отправляем сообщение
    server.quit()
    return 0


# поместить сообщение в файл
def file_in(str):
    f = open("C:/Minor_webapp/app/data/temp.txt", "w")
    f.write(str)
    f.close()


# получение и сохранение передаваемых устройством сигналов
def file_terminal_in():
    # Script listens to serial port and writes contents into a file
    # requires pySerial to be installed
    import serial

    # установка значений переменных по умолчанию

    # взятие последней геолокации пользователя
    f = open("C:/Minor_webapp/app/data/location.txt", 'r')
    tmp = f.read()
    location = tmp.split(' ')  # разделение координат
    print(location)
    print("def location a - " + location[0])
    print("def location b - " + location[1])
    f.close()

    Latitude = location[0]
    Longitude = location[1]

    # взятие постеледней метки времени известной геолокации
    f = open("C:/Minor_webapp/app/data/location_time.txt", 'r')
    tmp = f.read()
    location_time = tmp.split(' ')  # разделение координат
    print("def location_time - " + location_time[0])
    print("def location_time - " + location_time[1])
    f.close()

    Date = [location_time[0], location_time[1]]

    # взятие последних данных пульса
    f = open("C:/Minor_webapp/app/data/Pulse.txt", 'r')
    tmp = f.read()
    pulse = tmp.split(' ')  # разделение координат

    print("def pulse - " + pulse[0])
    print("def pulse_time - " + pulse[1] + " " + pulse[2])
    tmp = pulse[1] + " " + pulse[2]
    f.close()

    Pulse = [pulse[0], tmp]

    serial_port = 'COM4';
    baud_rate = 9600;  # In arduino, Serial.begin(baud_rate)
    # write_to_file_path = "output.txt";
    # output_file = open(write_to_file_path, "w+");
    ser = serial.Serial(serial_port, baud_rate)
    while True:
        line = ser.readline();
        line = line.decode("utf-8")  # ser.readline returns a binary, convert to string
        # output_file.write(line);

        # задержка в 1 сек
        import time
        time.sleep(1)

        # передача лога в общий файл GPS
        f = open("C:/Minor_webapp/app/data/GPS.txt", "w")
        f.write(line)
        f.close()

        # сохранение данных местоположения
        if line.startswith("GPS is not connected to satellites!!!"):
            print("Search for satellites")
            continue

        elif line.startswith("Latitude"):
            print("------ Latitude ------\n" + line + "-----------------");
            Latitude = line
            Latitude = Latitude.split("N")[1]
            Latitude = Latitude.strip()
            # print("1 - " + Latitude)

        elif line.startswith("Longitude"):
            f = open("C:/Minor_webapp/app/data/location.txt", "w")
            print("------ Longitude ------\n" + line + "-----------------");
            Longitude = line
            Longitude = Longitude.split("E")[1]
            Longitude = Longitude.strip()
            # print("2 - " + Longitude)
            f.write(str(Latitude) + " " + str(Longitude))
            f.close()

        # сохранение данных времени получения последнего местоположения
        if line.startswith("Date"):
            tmp = line
            tmp.replace('Date:', '')
            tmp = tmp.strip()
            Date[0] = tmp

            # print("1 - " + Latitude)
        if line.startswith("Time"):
            tmp = line
            tmp.replace('Time:', '')
            tmp = tmp.strip()
            Date[1] = tmp

            # print("2 - " + Longitude)
            f = open("C:/Minor_webapp/app/data/location_time.txt", "w")
            f.write(str(Date[0]) + " " + str(Date[1]))
            f.close()

        # сохранение данных последнего значнния серцебиения
        if line.startswith("Pulse"):
            #print(line,  end="")
            tmp = line
            tmp.replace('Pulse:', '')
            tmp = tmp.strip()
            Pulse[0] = tmp
            # print("1 - " + Latitude)

            today = date.today()
            current_date_time = datetime.datetime.now()
            current_time = current_date_time.time()  # время
            # дата и время
            now = str(today.day) + "." + str(today.month) + "." + str(today.year) + " " + str(current_time)

            Pulse[1] = now
            Pulse[0] = Pulse[0].replace('Pulse: ', '')
            Pulse[0] = float(Pulse[0])
            Pulse[0] = Pulse[0]
            print(Pulse[0])
            f = open("C:/Minor_webapp/app/data/pulse.txt", "w")
            f.write(str(Pulse[0]) + " " + str(Pulse[1]))
            f.close()

    print("***** Работа с устройством завершена *****")


# Обработка получаемых по MQTT сообщений
def message_processing(msg):
    global siteLaunched
    if (msg == "go") & (siteLaunched == False):
        print("***** Запуск сайта *****")
        siteLaunched = True
        os.system("python C:/Minor_webapp/app/Site.py")
        print("***** Работа с сайтом прекращена *****")

    elif (msg == "go") & (siteLaunched == True):
        print("Сайт должен быть уже запущен!")

    elif msg == "SOS":
        print("Получен сигнал SOS!\nВысылаю сообщение на сайт!")
    else:
        print("Получен неизвесный сигнал!")
        print("\033[33m {}".format(msg))  # вывод неизвесного сигнала жёлтым цветом
        file_in(msg)


# поток запускает веб сервер
def potock1(i):
    print("\n-----------------\n"
          "Поток %i стартовал\n"
          "-----------------\n" % i)
    message_processing("go")


# поток запускает чтение данных с устройства
def potock2(i):
    print("\n-----------------\n"
          "Поток %i стартовал\n"
          "-----------------\n" % i)
    file_terminal_in()


# запуск потоков
th1 = Thread(target=potock1, args=(1,))
th1.start()

th2 = Thread(target=potock2, args=(2,))
th2.start()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("mqtt.fluux.io", 1883, 60)

client.loop_forever()
