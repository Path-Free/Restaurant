from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import sqlite3 as sl
import json
import datetime
from tokens import bot, group_chat_id

con = sl.connect('stolovka.db', check_same_thread=False)

enter_keyboard = ReplyKeyboardMarkup()
enter_keyboard.row(KeyboardButton("Регистрация 📝"), KeyboardButton("Войти 🔓"))
lobby_keyboard = ReplyKeyboardMarkup()
lobby_keyboard.row(KeyboardButton("Меню 📖"), KeyboardButton("Корзина 🛒"), KeyboardButton("Поддержка 💡"))
lobby_keyboard.add(KeyboardButton("Мои заказы 📒"))
cats_keyboard = InlineKeyboardMarkup()
with con:
    data = con.execute("SELECT * FROM CATEGORIES").fetchall()
for x in data:
    cats_keyboard.add(InlineKeyboardButton(x[1], callback_data="c" + str(x[0])))
order_key = InlineKeyboardMarkup()
order_key.add(InlineKeyboardButton("🔘", callback_data="o"))


def conf_order(id):
    conf_keyb = InlineKeyboardMarkup()
    conf_keyb.add(InlineKeyboardButton("✅", callback_data="y" + str(id)))
    return conf_keyb


def good_page(list_of_data, n, count=1, flag_step="s", flag_buy="b", flag_add="a", flag_plus="+", flag_minus="-"):
    slider_keyb = InlineKeyboardMarkup()
    slider_keyb.row(
        InlineKeyboardButton("➖", callback_data=flag_minus + str(n)),
        InlineKeyboardButton(f"{count}", callback_data="hui"),
        InlineKeyboardButton("➕", callback_data=flag_plus + str(n))
    )
    slider_keyb.row(
        InlineKeyboardButton("Заказать 💵", callback_data=flag_buy + str(n)),
        InlineKeyboardButton("Добавить в корзину 🛒", callback_data=flag_add + str(n))
    )
    if n == 0 and len(list_of_data) > (n + 1):
        slider_keyb.add(InlineKeyboardButton("Следующее блюдо ➡️", callback_data=flag_step + str(n + 1)))
    elif n == len(list_of_data) - 1:
        slider_keyb.add(InlineKeyboardButton("⬅️ Предыдущее блюдо", callback_data=flag_step + str(n - 1)))
    else:
        slider_keyb.row(
            InlineKeyboardButton("⬅️ Предыдущее блюдо", callback_data=flag_step + str(n - 1)),
            InlineKeyboardButton("Следующее блюдо ➡️", callback_data=flag_step + str(n + 1))
        )
    return slider_keyb


def cart(x, cart_flag="k"):
    cart_keyboard = InlineKeyboardMarkup()
    cart_keyboard.row(
        InlineKeyboardButton("🗑", callback_data=cart_flag + "0" + str(x[0])),
        InlineKeyboardButton("➖", callback_data=cart_flag + "-" + str(x[0])),
        InlineKeyboardButton(f"{x[2]}", callback_data="hui"),
        InlineKeyboardButton("➕", callback_data=cart_flag + "+" + str(x[0]))
    )
    return cart_keyboard


list_of_data = {}


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        with con:
            data = \
                con.execute(f"SELECT EXISTS(SELECT id FROM USERS WHERE tg_id = '{message.from_user.id}')").fetchone()[0]
        if not data:
            bot.send_message(message.from_user.id, "Добро пожаловать в проект 'РЕСТОРАН'!", reply_markup=enter_keyboard)
        else:
            bot.send_message(message.from_user.id, "Рады снова видеть вас в проекте 'РЕСТОРАН'!",
                             reply_markup=lobby_keyboard)

    elif message.text == "Регистрация 📝" or message.text == "/register":
        msg = bot.send_message(message.from_user.id, "Придумайте логин:")
        bot.register_next_step_handler(msg, re_login)

    elif message.text == "Войти 🔓" or message.text == "/sign_in":
        msg = bot.send_message(message.from_user.id, "Введите логин:")
        bot.register_next_step_handler(msg, en_login)

    elif message.text == "Выйти" or message.text == "/sign_out":
        with con:
            con.execute(f"UPDATE USERS SET tg_id = NULL WHERE tg_id = '{message.from_user.id}'").fetchall()
        bot.send_message(message.from_user.id, "Вы вышли из учётной записи.", reply_markup=enter_keyboard)

    elif message.text == "Меню 📖" or message.text == "/menu":
        bot.send_message(message.from_user.id, "Категории:", reply_markup=cats_keyboard)

    elif message.text == "Корзина 🛒" or message.text == "/cart":
        with con:
            data = \
                con.execute(f"SELECT EXISTS(SELECT id FROM USERS WHERE tg_id = '{message.from_user.id}')").fetchone()[0]
        if data:
            with con:
                data = con.execute("SELECT EXISTS (SELECT 1 FROM CART)").fetchone()[0]
            if not data:
                bot.send_message(message.from_user.id, "В вашей корзине пока пусто 😔")
            else:
                with con:
                    data = con.execute("SELECT * FROM CART").fetchall()
                for x in data:
                    with con:
                        name = con.execute(f"SELECT name FROM GOODS WHERE id = {x[1]}").fetchone()
                    bot.send_message(message.from_user.id, name, reply_markup=cart(x))
                bot.send_message(message.from_user.id, "Оформить!", reply_markup=order_key)
        else:
            bot.send_message(message.from_user.id, "Для просмотра корзины необходимо войти в существующий аккаунт.",
                             reply_markup=enter_keyboard)

    elif message.text == "Мои заказы 📒" or message.text == "/orders":
        with con:
            user_id = \
                con.execute(f"SELECT id FROM USERS WHERE tg_id = '{message.from_user.id}'").fetchone()[0]
        if user_id:
            with con:
                data = con.execute(f"SELECT * FROM ORDERS WHERE user_id = {user_id}").fetchall()
            if data:
                for x in data:
                    with con:
                        status = con.execute(f"SELECT name FROM STATUSES WHERE id = {x[3]}").fetchone()[0]
                    bot.send_message(message.from_user.id,
                                     f"Заказ №{x[0]}. Время заказа: {x[2]}. Статус заказа: {status}.")
            else:
                bot.send_message(message.from_user.id, "Ваша история заказов пока что пуста 😔")
        else:
            bot.send_message(message.from_user.id, "Для просмотра заказов необходимо войти в существующий аккаунт.",
                             reply_markup=enter_keyboard)

    elif message.chat.id == group_chat_id:
        if message.text[:4] == "next":
            id = message.text[4:]
            with con:
                data = con.execute(f"SELECT status FROM ORDERS WHERE id = {id}").fetchone()[0]
                if data < 4:
                    con.execute(f"UPDATE ORDERS SET status = status + 1 WHERE id = {id}")
                    data = con.execute(f"SELECT status FROM ORDERS WHERE id = {id}").fetchone()[0]
                    status = con.execute(f"SELECT name FROM STATUSES WHERE id = {data}").fetchone()[0]
                    bot.send_message(group_chat_id, f"Статус заказа №{id}: {status}.")
                else:
                    bot.send_message(group_chat_id, f"Статус заказа №{id} не может быть повышен.")

    # elif message.text == "Поддержка 💡" or message.text == "/help":


def re_login(message):
    login = message.text
    with con:
        data = con.execute(f"SELECT EXISTS (SELECT id FROM USERS WHERE login = '{login}')").fetchone()[0]
    if not data:
        msg = bot.send_message(message.from_user.id, "Придумайте пароль:")
        bot.register_next_step_handler(msg, re_password, login)
    else:
        bot.send_message(message.from_user.id, "Такой логин уже зарегистрирован, желаете войти?",
                         reply_markup=enter_keyboard)


def re_password(message, login):
    password = message.text
    sql_insert = "INSERT INTO USERS (login, password) values(?, ?)"
    with con:
        con.execute(sql_insert, [f"{login}", f"{password}"])
    bot.send_message(message.from_user.id, "Вы успешно зарегистрированы! Чтобы войти нажмити кнопку 'Войти'",
                     reply_markup=enter_keyboard)


def en_login(message):
    login = message.text
    with con:
        data = con.execute(f"SELECT EXISTS (SELECT id FROM USERS WHERE login = '{login}')").fetchone()[0]
    if data:
        msg = bot.send_message(message.from_user.id, "Введите пароль:")
        bot.register_next_step_handler(msg, en_password, login)
    else:
        msg = bot.send_message(message.from_user.id, "Такой логин не существует, попробуйте снова:")
        bot.register_next_step_handler(msg, en_login)


def en_password(message, login):
    global list_of_data
    password = message.text
    with con:
        data = con.execute(
            f"SELECT EXISTS (SELECT id FROM USERS WHERE login = '{login}' AND password = '{password}')").fetchone()[0]
    if data:
        with con:
            con.execute(f"UPDATE USERS SET tg_id = '{message.from_user.id}' WHERE login = '{login}'")
        bot.send_message(message.from_user.id, "Успешно!", reply_markup=lobby_keyboard)
        list_of_data[message.from_user.id] = []
    else:
        msg = bot.send_message(message.from_user.id, "Неправильный пароль, попробуйте снова:")
        bot.register_next_step_handler(msg, en_password, login)


def or_address(message, id):
    address = message.text
    with con:
        con.execute(f"UPDATE USERS SET last_address = '{address}' WHERE id = {id}")


def or_tel(message, id):
    tel = message.text
    with con:
        con.execute(f"UPDATE USERS SET tel = {tel} WHERE id = {id}")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global list_of_data
    bot.answer_callback_query(callback_query_id=call.id, )
    if call.data[0] == "c":
        with con:
            list_of_data[call.message.chat.id] = con.execute(
                f"SELECT * FROM GOODS WHERE category = {call.data[1:]}").fetchall()
        with open(f"images/{list_of_data[call.message.chat.id][0][0]}.jpg", "rb") as image:
            bot.send_photo(call.message.chat.id, photo=image,
                           caption=f"{list_of_data[call.message.chat.id][0][1]} 🍽\n{list_of_data[call.message.chat.id][0][3]}\n{list_of_data[call.message.chat.id][0][2]} руб.",
                           reply_markup=good_page(list_of_data[call.message.chat.id], 0))
    elif call.data[0] == "s":
        n = int(call.data[1:])
        with open(f"images/{list_of_data[call.message.chat.id][n][0]}.jpg", "rb") as image:
            bot.edit_message_media(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                   media=types.InputMediaPhoto(image))
            bot.edit_message_caption(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                     caption=f"{list_of_data[call.message.chat.id][n][1]} 🍽\n{list_of_data[call.message.chat.id][n][3]}\n{list_of_data[call.message.chat.id][n][2]} руб.",
                                     reply_markup=good_page(list_of_data[call.message.chat.id], n))
    elif call.data[0] == "+":
        n = int(call.data[1:])
        count = int(call.message.json["reply_markup"]["inline_keyboard"][0][1]["text"])
        bot.edit_message_caption(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                 caption=call.message.json["caption"],
                                 reply_markup=good_page(list_of_data[call.message.chat.id], n, count + 1))
    elif call.data[0] == "-":
        n = int(call.data[1:])
        count = int(call.message.json["reply_markup"]["inline_keyboard"][0][1]["text"])
        if count > 1:
            bot.edit_message_caption(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                     caption=call.message.json["caption"],
                                     reply_markup=good_page(list_of_data[call.message.chat.id], n, count - 1))
    elif call.data[0] == "b" or call.data[0] == "a":
        with con:
            user_id = con.execute(f"SELECT id FROM USERS WHERE tg_id = '{call.message.chat.id}'").fetchone()[0]
        if user_id:
            n = int(call.data[1:])
            count = int(call.message.json["reply_markup"]["inline_keyboard"][0][1]["text"])
            good_id = list_of_data[call.message.chat.id][n][0]
            if call.data[0] == "b":
                bot.send_message(call.message.chat.id, "Ваш заказ ⬇️")
                with con:
                    con.execute(f"DELETE FROM CART")
                    con.execute(
                        f"INSERT INTO CART (id, good_id, count, user_id) VALUES (1, {good_id}, {count}, {user_id})")
                    data = con.execute("SELECT * FROM CART").fetchall()
                for x in data:
                    with con:
                        name = con.execute(f"SELECT name FROM GOODS WHERE id = {x[1]}").fetchone()
                    bot.send_message(call.message.chat.id, name, reply_markup=cart(x))
                bot.send_message(call.message.chat.id, "Оформить!", reply_markup=order_key)
            elif call.data[0] == "a":

                with con:
                    data = con.execute(f"SELECT EXISTS (SELECT id FROM CART WHERE good_id = {good_id})").fetchone()[0]
                    if data:
                        con.execute(f"UPDATE CART SET count = count + {count}")
                    else:
                        con.execute(
                            f"INSERT INTO CART (good_id, count, user_id) VALUES ({good_id}, {count}, {user_id})")
        else:
            bot.send_message(call.message.chat.id, "Чтобы сделать заказ, необходимо войти в существуюший аккаунт.",
                             reply_markup=enter_keyboard)
    elif call.data[0] == "k":
        if call.data[1] == "+":
            with con:
                con.execute(f"UPDATE CART SET count = count + 1 WHERE id = {call.data[2:]}")
                x = con.execute(f"SELECT * FROM CART WHERE id = {call.data[2:]}").fetchone()
            bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                  text=call.message.json["text"], reply_markup=cart(x))
        elif call.data[1] == "-":
            with con:
                count = con.execute(f"SELECT count FROM CART WHERE id = {call.data[2:]}").fetchone()[0]
            if count > 1:
                with con:
                    con.execute(f"UPDATE CART SET count = count - 1 WHERE id = {call.data[2:]}")
                    x = con.execute(f"SELECT * FROM CART WHERE id = {call.data[2:]}").fetchone()
                    bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                          text=call.message.json["text"], reply_markup=cart(x))
        elif call.data[1] == "0":
            with con:
                con.execute(f"DELETE FROM CART WHERE id = {call.data[2:]}")
            bot.delete_message(message_id=call.message.message_id, chat_id=call.message.chat.id)
    elif call.data[0] == "o":
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        with con:
            data = con.execute(
                f"SELECT * FROM CART WHERE user_id = (SELECT id FROM USERS WHERE tg_id = {call.message.chat.id})").fetchall()
            user_id = con.execute(f"SELECT id FROM USERS WHERE tg_id = {call.message.chat.id}").fetchone()[0]
            address = con.execute(f"SELECT last_address FROM USERS WHERE id = {user_id}").fetchone()[0]
            tel = con.execute(f"SELECT tel FROM USERS WHERE id = {user_id}").fetchone()[0]
            if address and tel:
                con.execute(f"INSERT INTO ORDERS (user_id, date_time) VALUES ({user_id}, '{now}')")
                con.execute(f"DELETE FROM CART WHERE user_id = {user_id}")
                order_id = \
                    con.execute(f"SELECT id FROM ORDERS WHERE user_id = {user_id} AND date_time = '{now}'").fetchone()[
                        0]
                with open(f"orders/{order_id}.json", "w") as write_file:
                    json.dump(data, write_file)
                bot.send_message(call.message.chat.id, f"Заказ №{order_id} в обработке, ожидайте!")
                bot.send_message(group_chat_id, f"Заказ №{order_id} ожидает подтверждения!",
                                 reply_markup=conf_order(order_id))
            elif not address:
                msg = bot.send_message(call.message.chat.id, f"Для оформления необходимо ввести адресс доставки:")
                bot.register_next_step_handler(msg, or_address, user_id)
            elif not tel:
                msg = bot.send_message(call.message.chat.id, f"Для оформления необходимо ввести ваш номер телефона:")
                bot.register_next_step_handler(msg, or_tel, user_id)

    elif call.data[0] == "y":
        with con:
            con.execute(f"UPDATE ORDERS SET status = 2 WHERE id = {call.data[1:]}")
        bot.send_message(group_chat_id, f"Заказ №{call.data[1:]} подтверждён.")


print("Ready")
bot.infinity_polling()
