import os

from flask import Flask, url_for, request, session, flash, render_template, redirect, make_response
# from flask_login import current_user
from datetime import timedelta
import pandas
import pandas as pd

from app.forms import LoginForm

"""
http://127.1.0.0:5000 при обновлении в CSS необходимо изменить цифру в ссылке для обновления отображения кода
"""

############## Блок кода с установкой значений переменных и конфигураций в началное положение ##############


app = Flask(__name__)  # создание объекта Flask
# app.config.from_object('config')
app.secret_key = "0xx2r45y74f4"  # Установка ключа для отладки
app.permanent_session_lifetime = timedelta(minutes=30)  # Настройка времени сессии

msd = "Default_msg"  # сообщение для работы сайта
location = ["0.0", "0.0"]
location_time = ["0", "0:0:0"]
latitude = "0.0"
longitude = "0.0"
pulse = ["0", "0:0:0"]
GPS = 0  # лог GPS
sost = "Требуется настройка"


# взятие последней геолокации пользователя
def updateLocation():
    global location
    global latitude
    global longitude
    f = open("C:/Minor_webapp/app/data/location.txt", 'r')
    tmp = f.read()
    location = tmp.split(' ')  # разделение координат
    #print(location)
    print("def location 1 - " + location[0])
    print("def location 2 - " + location[1])
    f.close()

    latitude = location[0]
    longitude = location[1]


# взятие постеледней метки времени известной геолокации
def updateLocation_time():
    global location_time
    f = open("C:/Minor_webapp/app/data/location_time.txt", 'r')
    tmp = f.read()
    location_time = tmp.split(' ')  # разделение координат
    print("def location_time - " + location_time[0])
    print("def location_time - " + location_time[1])
    f.close()


# взятие последних данных пульса
def updatePulse():
    global pulse
    f = open("C:/Minor_webapp/app/data/Pulse.txt", 'r')
    tmp = f.read()
    pulse = tmp.split(' ')  # разделение координат
    # pulse[1] = ''.join(reversed(str(pulse[1])))
    pulse[2] = pulse[2].split(".")[0]
    print("def pulse - " + pulse[0])
    print("def pulse_time - " + pulse[1] + " " + pulse[2])
    f.close()
    return 0


updateLocation()
updateLocation_time()
updatePulse()


# чтение данных из временного файла (нужно для отладки работы сайта)
def file_out():
    f = open("C:/Minor_webapp/app/data/temp.txt", 'r')
    global msg
    msg = f.read()
    f.close()
    return 0


# взятие всех данных, передаваемых GPS/Glonass Модулем (Лог GPS)
def file_GPS_out():
    global GPS
    f = open("C:/Minor_webapp/app/data/GPS.txt", 'r')
    tmp = f.read()
    GPS = tmp
    f.close()
    return 0


# Получение состояния пользователя
def updateSost():
    global sost
    global pulse
    f = open("C:/Minor_webapp/app/data/sost.txt", 'r')
    sost = f.read()
    f.close()

    if 50 < float(pulse[0]) < 100:
        sost = "Норма"
    elif float(pulse[0]) < 0 or float(pulse[0]) > 250:
        sost = "Трбуется настройка"
    else:
        sost = "Экстра"
    return sost


"""
    global msg
    if msg == "SOS":
        sost = "Требуется помощь"
"""


# Получение таблицы данных пользователей
# пока не используется
def getExel():
    excel_data_df = pandas.read_excel('users.xlsx', sheet_name='Пользователи')
    print(excel_data_df)


@app.route('/')
@app.route('/index')
def index():
    """
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    """
    return render_template('Login M.html')

@app.route('/Register')
def reg():
    return render_template('Register.html')

@app.route('/Register-rebenoc')
def reg_reb():
    return render_template('Register-rebenoc.html')

@app.route('/Child')
def child():
    return render_template('Child.html', latitude=latitude, longitude=longitude, batar=100)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html',  title='Sign In', form=form)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # запуск сайта

print("***** Работа с сайтом завершена *****")
