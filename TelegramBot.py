import telebot                      # - Билиотека для работы с телеграм ботом
from telebot import types
import csv                          # - Библиотека для работы с CSV файлами
import datetime                     # - Библиотека для работы со временем и датой (текущей)
from datetime import datetime,date,time
import time
from multiprocessing import *
import threading
import schedule
import config                        # - Конфиг для своего телеграм бота и базы данных ( с токеном и названием)
import mysql.connector
from mysql.connector import Error

#import Celery                       
#from celery import Celery
#import array                       # - Библиотека для работы с массивами(если необходимо)
#import pypi
# ---------------- ПОЯСНЕНИЯ ---------------------- #
#message.chat.id - сообщение в чат бота
#config.config['private_message_chat_id'] - сообщение мне

# ---------------- PRIVATE VARIABLES ---------------------- #

# Содержание ключа бота
TelegramBot = telebot.TeleBot(config.config['token']) # - Вариант использования токена с файла config
Players = []                # Массив игроков локальный ( Оперативная память)
BirthdayPlayers = []        # Массив игроков, у кого будет день рождение в этом месяце
linecount = 0               # Подсчет линий
output_message_day = ""     # Сообщение для отправки количество людей у кого сегодня д.р.
output_message_month = ""   # Сообщение для отправки количество людей у кого в этом месяце д.р.
output_message_list = ""    # Список всех игроков
flag_update_data = False
flag_data_connection = False
SQLDatabase = mysql.connector
filenameWrite = "BoarTeamSorted.csv"
filenameRead = "BoarTeam.csv"

now = datetime.now() # Данные для хранения даты

create_movies_table_query = """
INSERT INTO ActiveHockeyPlayers (id, Surname, Name, MiddleName, PlayerNumber, Birthday, IsActive, DatePlayerJoin, DatePlayerLeave Telephone)
VALUES ('5', 'Иванов', 'Иван', 'Иванович', '112', '2022-01-01', '1', '2022-09-10', '2022-09-10', '71234567890')
"""

# Для работы с высвечивающейся клавиатуры
#keyboard1 = telebot.types.ReplyKeyboardMarkup(<span class="hljs-keyword">True</span>, <span class="hljs-keyword">True</span>)
#keyboard1 = telebot.types.ReplyKeyboardMarkup(one_time_keyboard= "true",resize_keyboard= "true")
#keyboard1.row('ДР','Привет', 'Пока',"Hello","Nice","New")
#keyboard1.row()
#const bot = New telebot()
# Функция проверки дней рождений каждый день

def CheckBirthdayEveryDay(message):
    global output_message_day
    for i in range(len(Players)):
         if (int(Players[i].month) == int(now.month)):
                output_message_day += "Сегодня день рождение празднует: \n\n"
                if (int(Players[i].day) == now.day):
                    #output_message_day += "Сегодня день рождение празднует: \n"
                    output_message_day += "\U0001F381 " # Unicode emoji gift
                    output_message_day += (str(Players[i].surname) + " " + str(Players[i].name) + " " + str(Players[i].day + "-" + str(Players[i].month) + "-" + str(Players[i].year)))
                    output_message_day += " \U0001F381 \n" # Unicode emoji gift
    if (output_message_day != ""): # - Если нет дней рождений и сообщение пустое, то выводить ничего не нужно
        TelegramBot.send_message(message.chat.id, output_message_day)
    output_message_day = ""

#----------------- START PROCESSING -----------------------------#
def start_process():#Запуск Process
    p1 = Process(target=P_schedule.start_schedule, args=()).start()

class P_schedule(): # Class для работы с schedule
    def start_schedule(): #Запуск schedule
        ######Параметры для schedule######
        schedule.every().day.at("09:00").do(P_schedule.checkBirthdayEveryDay_thread) # Проверка функции в определенное время
        #schedule.every(1).minutes.do(P_schedule.checkBirthdayEveryDay_thread) # Проверка функции с интервалом в 1 минуту
        ##################################
        
        while True: #Запуск цикла
            schedule.run_pending()
            time.sleep(1)
 
    ####Функции для выполнения заданий по времени  
    def checkBirthdayEveryDay_thread():
        CheckBirthdayEveryDay()
    #def send_message2():
        #TelegramBot.send_message(config.config['private_message_chat_id'], 'Отправка сообщения через определенное время')
    ################
# ---------------- TELEGRAM BOTS COMMANDS ---------------------- #
# ---------------- DATA BASE FUNCTIONS ---------------------- #
def connect():
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host=config.config['db_ip'],
                                       user=config.config['db_userName'],
                                       password=config.config['db_password'])
        if conn.is_connected():
            print('Connected to MySQL database')
            flag_data_connection = True
            SQLDatabase = conn
            

    except Error as e:
        print(e)
        TelegramBot.send_message(config.config['private_message_chat_id'], 'Соединение с базой данных отсутствует')

def PullDataFromDatabase():
    if flag_data_connection == True:
        with SQLDatabase.cursor() as cursor:
            cursor.execute(create_movies_table_query)
            SQLDatabase.commit()
    


# Ответ бота на команды через "/" и вывод клавиатуры
# @TelegramBot.message_handler(commands=['cmd'])
# def start_message(message):
    # markup_inline = types.InlineKeyboardMarkup()
    # item1 = types.InlineKeyboardButton(text = 'Да',callback_data='yes')
    # item2 = types.InlineKeyboardButton(text = 'Нет',callback_data='No')
    # markup_inline(item1,item2)
    # TelegramBot.send_message(message.chat.id, 'Привет, ты написал мне cmd c кнопками', reply_markup=markup_inline)


# ============= TEST: ===================== #
# ============= TEST: ===================== #

# @TelegramBot.message_handler(content_types=["text"])
# def repeat_all_messages(message): # Название функции не играет никакой роли
#     keyboard = telebot.types.InlineKeyboardMarkup()
#     TelegramBot.send_message(message.chat.id, message.text)

# Ответ бота на команды через "/" и Вывод информации о сообщении
@TelegramBot.message_handler(commands=['msg_info'])
def start(message):
    print(message)

@TelegramBot.message_handler(commands=['check_database'])
def CheckDatabaseStatus(message):
    if flag_data_connection == True:
        TelegramBot.send_message(message.chat.id, 'База данных подключена и запущена')
    elif flag_data_connection == False:
        TelegramBot.send_message(message.chat.id, 'База данных НЕ подключена')


# Ответ бота на команды через "/"
@TelegramBot.message_handler(commands=['start']) # /start
def start_message(message):
    TelegramBot.send_message(message.chat.id, 'Привет, ты написал мне /start')
    TelegramBot.send_message(message.chat.id, message.text) # - по факту считанные данные
#threading.Thread(target = start_message, args = (1,), daemon = True).start()

@TelegramBot.message_handler(commands=['savecsv']) # /savecsv
def saveToCSV(message):
    try:
        with open(filenameWrite, "w", newline="") as file:
            fieldnames = ["Фамилия","Имя","день","месяц","год"] 
            writer = csv.DictWriter(file,delimiter = ";", lineterminator="\r",fieldnames = fieldnames)
            for player in Players:
                writer.writerow({"Фамилия":player.surname,"Имя": player.name,"день":player.day,"месяц":player.month,"год":player.year})
        TelegramBot.send_message(message.chat.id, 'Файл сохранен')
    except:
        print("File Already opened")
        TelegramBot.send_message(message.chat.id, "Файл открыт другим пользователем")
    
# Ответ бота на текстовые сообщения
@TelegramBot.message_handler(content_types=['text'])
def send_text(message):
    print(message.chat.id)
    #if message.text.lower() == 'привет':
        #TelegramBot.send_message(message.chat.id, 'Привет, мой создатель')
        #checkNearBirthday()
    #if message.text.lower() == 'пока':
        #TelegramBot.send_message(message.chat.id, 'Прощай, создатель')
    if message.text.lower() == 'др':
        checkNearBirthday(message)
    elif message.text.lower() == 'список':
        PrintAllPlayers(message)

        # TelegramBot.send_message(config.config['private_message_chat_id'], 'Привет, мой создатель')
        # TelegramBot.send_message(config.config['private_message_chat_id'], <span class="hljs-string">'Текст сообщения'</span>)

# @TelegramBot.message_handler(func=lambda message: False) #cause there is no message
# def saturday_message(m):
#     global flag_update_data
#     global now
#     # if (now.date().weekday() == 5) and (now.time() == time(8,0)):
#     #     TelegramBot.send_message(message.chat_id, 'Wake up!')
#     if(now.time()>=time(18,29)):
#         #flag_update_data = True
#         TelegramBot.send_message(config.config['private_message_chat_id'], 'Wake up!')
#threading.Thread(target = saturday_message, args = (1,), daemon = True).start()

# Функция для сортировки игроков по дате рождения
def sort_by_birthday(e):
    return e.day

# Функция для сортировки игроков по фамилии
def sort_by_surname(index):
    return index.surname
# ---------------- LOCAL CLASS PARAMETERS ---------------------- #
class BoarPlayer():
    """Описание игрока"""
    def __init__(self,name,surname,day,month,year):
        self.name = name            # 00
        self.surname = surname      # 01
        self.day = day              # 02
        self.month = month          # 03
        self.year = year            # 04
    def __repr__(self):
        return f"{self.surname} {self.name} {self.day}-{self.month}-{self.year}"

# ---------------- LOGIC CSV FILE ---------------------- #
#with open("F:\Python_projects\TelegramBot\BoarTeam.csv", newline='') as csvfile:
try:
    with open(filenameRead, newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';')
        for row in spamreader:
            Player = BoarPlayer(row['Имя'],row['Фамиля'],row['день'],row['месяц'],row['год'])
            Players.append(Player)
            linecount += 1
            #print(', 'ya.join(row))
            #print(row['месяц'])
            # if (row[])
        Players = sorted(Players, key=sort_by_surname)
except:
    print("File Already opened")
    TelegramBot.send_message(config.config['private_message_chat_id'], "Файл открыт другим приложением")
    #Players = sorted(Players, key=attrge)
    
# ---------------- PRIVATE FUNCTIONS ---------------------- #



#def cancelThread():
    #print("Мы перешли в функцию отмены)")
    #threading.Timer(10, checkNearBirthday).start()

# Функция проверки дней рождений в месяце
def checkNearBirthday(message):
    global output_message_month
    global BirthdayPlayers
    NewArray = []
    for i in range(len(Players)):
        if (int(Players[i].month) == int(now.month)):
            if (int(Players[i].day) > now.day):
                #print("В этом месяце празднует день рождение",Players[i].surname,Players[i].name,Players[i].day)
                BirthdayPlayers.append(Players[i]) # - Заполнили массив, у кого в этом месяце день рождение                    
    if (len(BirthdayPlayers) != 0):
        BirthdayPlayers = sorted(BirthdayPlayers, key=sort_by_birthday)
        output_message_month += "В этом месяце празднуют день рождение: \n\n"
        for i in range(len(BirthdayPlayers)):
            #output_message_month += "\U0001F381 " # Unicode emoji gift
            output_message_month += (str(BirthdayPlayers[i].surname) + " " + str(BirthdayPlayers[i].name) + " " + str(BirthdayPlayers[i].day + "-" + str(BirthdayPlayers[i].month) + "-" + str(BirthdayPlayers[i].year) + " \n"))
            #output_message_month += " \U0001F381 \n" # Unicode emoji gift
        TelegramBot.send_message(message.chat.id, output_message_month)
        BirthdayPlayers.clear()
    else:
        TelegramBot.send_message(message.chat.id, "В этом месяце дней рождений нет")
    output_message_month = ""
    
    # TelegramBot.register_next_step_handler(config.config['private_message_chat_id'], cancelThread())
    


def PrintAllPlayers(message):
    global Players
    global output_message_list
    for i in range(len(Players)):
        #print(Players[i])
        #output_message_list +=i + ". " + Players[i] + "\n"
        output_message_list += str(i+1) + ". "+str(Players[i]) + "\n"
    TelegramBot.send_message(message.chat.id, output_message_list)
    output_message_list = "" # - обнулянем список
    
# TODO Сделать отсортированный список по месяцам,затем по дате, пока не работает line 93, in <module> TypeError: '<' not supported between instances of 'BoarPlayer' and 'BoarPlayer'
#PlayerSorted = sorted(Players) # Отсартированный список по дням
#print(PlayerSorted) # вывод отсортированного списка по дням
#checkNearBirthday() # -Запуск нашей функции ( в дальнейшем она будет в верхних функциях)

#threading.Timer(10, checkNearBirthday).start()
# schedule.every().day.at("10:41").do(checkNearBirthday)
#TelegramBot.polling(none_stop=True)

if __name__ == '__main__':
    start_process()
    connect()
    try:
        TelegramBot.polling(none_stop=True)
    except:
        pass
# def WhileSchedule():
#     time.sleep(1)
#     schedule.run_pending()

# while True: # этот цикл отсчитывает время. Он обязателен.
#     print("Before Polling")
#     TelegramBot.polling()
#     print("After Pooling")
    #TelegramBot.polling() # - Функция для циклического опроса параметров
    
# ---------------- NOTES ---------------------- #
#print(len(Players))            # - Количество игроков в массиве(листе)
#print(Players[0].day)          # - Вывести день рождения первого игрова
#print(datetime.date())         # - Вывести текующую дату
# for x in range(1,10):         # - Обработчик как в си for (int i = 0; i<10; i++)
#     Players.append()




