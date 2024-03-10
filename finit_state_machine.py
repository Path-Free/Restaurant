import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import sqlite3 as sl
import json
import datetime
import tokens

con = sl.connect('stolovka.db', check_same_thread=False)
bot = telebot.TeleBot(tokens.bot_token)
group_chat_id = -959200510

info_list = ["Придумайте логин:", "Придумайте пароль:", "Введите адрес доставки:","Введите вашу электронную почту:", "Введите ваш номер телефона:"]
user_list = None




@bot.message_handler(content_types=['text'])
def start(message):
    global user_list, info_list
    if message.text == '/register':
        user_list = []
    if user_list != None:
        if len(user_list) == len(info_list):
            "Справился, молодец!"
            print(user_list)
            user_list = None
        else:
            print(info_list[len(user_list)])
            user_list.append(message.text)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global list_of_data
    bot.answer_callback_query(callback_query_id=call.id, )

print("Ready")
bot.infinity_polling()
