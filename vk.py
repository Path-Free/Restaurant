from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
import sqlite3 as sl
from tokens import bot, group_chat_id, vk, longpoll
import json
import datetime

con = sl.connect('stolovka.db', check_same_thread=False)

# with con:
#     data = con.execute("SELECT * FROM USERS").fetchall()
# print(data)

enter_keyboard = VkKeyboard(one_time=False, inline=False)
enter_keyboard.add_button(label="Регистрация 📝", color=VkKeyboardColor.NEGATIVE, payload={"type": "text"})
enter_keyboard.add_button(label="Войти 🔓", color=VkKeyboardColor.NEGATIVE, payload={"type": "text"})
lobby_keyboard = VkKeyboard(one_time=False, inline=False)
lobby_keyboard.add_button(label="Меню 📖", color=VkKeyboardColor.NEGATIVE, payload={"type": "text"})
lobby_keyboard.add_button(label="Корзина 🛒", color=VkKeyboardColor.NEGATIVE, payload={"type": "text"})
lobby_keyboard.add_line()
lobby_keyboard.add_button(label="Мои заказы 📒", color=VkKeyboardColor.NEGATIVE, payload={"type": "text"})
cats_keyboard = VkKeyboard(one_time=False, inline=True)
with con:
    data = con.execute("SELECT * FROM CATEGORIES").fetchall()
for x in data:
    cats_keyboard.add_callback_button(label=x[1], color=VkKeyboardColor.SECONDARY, payload={"type": "c" + str(x[0])})
    if x != data[len(data) - 1]:
        cats_keyboard.add_line()

order_key = VkKeyboard(one_time=False, inline=True)
order_key.add_callback_button(label="🔘", color=VkKeyboardColor.SECONDARY, payload={"type": "o"})


def conf_order(id):
    conf_keyb = VkKeyboard(one_time=False, inline=True)
    conf_keyb.add_callback_button(label="✅", color=VkKeyboardColor.SECONDARY, payload={"type": "y" + str(id)})
    return conf_keyb


def good_page(list_of_data, n, count=1, flag_step="s", flag_buy="b", flag_add="a", flag_plus="+", flag_minus="-"):
    slider_keyb = VkKeyboard(one_time=False, inline=True)
    slider_keyb.add_callback_button(label="➖", color=VkKeyboardColor.SECONDARY,
                                    payload={"type": flag_minus + str(n), "count": str(count)})
    slider_keyb.add_callback_button(label=f"{count}", color=VkKeyboardColor.SECONDARY, payload={"type": "hui"})
    slider_keyb.add_callback_button(label="➕", color=VkKeyboardColor.SECONDARY,
                                    payload={"type": flag_plus + str(n), "count": str(count)})
    slider_keyb.add_line()
    slider_keyb.add_callback_button(label="Заказать 💵", color=VkKeyboardColor.SECONDARY,
                                    payload={"type": flag_buy + str(n), "count": str(count)})
    slider_keyb.add_callback_button(label="Добавить в корзину 🛒", color=VkKeyboardColor.SECONDARY,
                                    payload={"type": flag_add + str(n), "count": str(count)})
    slider_keyb.add_line()
    if n == 0 and len(list_of_data) > (n + 1):
        slider_keyb.add_callback_button(label="Следующее блюдо ➡️", color=VkKeyboardColor.SECONDARY,
                                        payload={"type": flag_step + str(n + 1)})
    elif n == len(list_of_data) - 1:
        slider_keyb.add_callback_button(label="⬅️ Предыдущее блюдо", color=VkKeyboardColor.SECONDARY,
                                        payload={"type": flag_step + str(n - 1)})
    else:
        slider_keyb.add_callback_button(label="⬅️ Предыдущее блюдо", color=VkKeyboardColor.SECONDARY,
                                        payload={"type": flag_step + str(n - 1)})
        slider_keyb.add_callback_button(label="Следующее блюдо ➡️", color=VkKeyboardColor.SECONDARY,
                                        payload={"type": flag_step + str(n + 1)})
    return slider_keyb


def cart(x, cart_flag="k"):
    cart_keyboard = VkKeyboard(one_time=False, inline=True)
    cart_keyboard.add_callback_button(label="🗑", color=VkKeyboardColor.SECONDARY,
                                      payload={"type": cart_flag + "0" + str(x[0])})
    cart_keyboard.add_callback_button(label="➖", color=VkKeyboardColor.SECONDARY,
                                      payload={"type": cart_flag + "-" + str(x[0])})
    cart_keyboard.add_callback_button(label=f"{x[2]}", color=VkKeyboardColor.SECONDARY, payload={"type": "hui"})
    cart_keyboard.add_callback_button(label="➕", color=VkKeyboardColor.SECONDARY,
                                      payload={"type": cart_flag + "+" + str(x[0])})
    return cart_keyboard


print("Ready")

list_of_data = {}
state_dict = {}

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj.message['text'] != '':
            if event.from_user:
                if event.obj.message['from_id'] not in state_dict.keys():
                    state_dict[event.obj.message['from_id']] = {"re_login": 0, "re_password": 0, "en_login": 0,
                                                                "en_password": 0, "or_address": 0, "or_tel": 0}
                with con:
                    data = \
                        con.execute(
                            f"SELECT EXISTS(SELECT id FROM USERS WHERE vk_id = '{event.obj.message['from_id']}')").fetchone()[
                            0]
                if event.obj.message['text'] == '/start':
                    if not data:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=enter_keyboard.get_keyboard(),
                            message="Добро пожаловать в проект 'РЕСТОРАН'!")
                    else:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=lobby_keyboard.get_keyboard(),
                            message="Рады снова видеть вас в проекте 'РЕСТОРАН'!")

                elif event.obj.message["text"] == "Регистрация 📝" or event.obj.message["text"] == "/register":
                    state_dict[event.obj.message['from_id']]["re_login"] = 1
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        message="Придумайте логин:")

                elif state_dict[event.obj.message['from_id']]["re_login"] == 1:
                    login = event.obj.message["text"]
                    with con:
                        data = con.execute(f"SELECT EXISTS (SELECT id FROM USERS WHERE login = '{login}')").fetchone()[
                            0]
                    if not data:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            message="Придумайте пароль:")
                        state_dict[event.obj.message['from_id']]["re_login"] = 0
                        state_dict[event.obj.message['from_id']]["re_password"] = 1
                    else:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=enter_keyboard.get_keyboard(),
                            message="Такой логин уже зарегистрирован, желаете войти?")
                        state_dict[event.obj.message['from_id']]["re_login"] = 0

                elif state_dict[event.obj.message['from_id']]["re_password"] == 1:
                    password = event.obj.message["text"]
                    sql_insert = "INSERT INTO USERS (login, password) values(?, ?)"
                    with con:
                        con.execute(sql_insert, [f"{login}", f"{password}"])
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=enter_keyboard.get_keyboard(),
                        message="Вы успешно зарегистрированы! Чтобы войти нажмити кнопку 'Войти'")
                    state_dict[event.obj.message['from_id']]["re_password"] = 0

                elif event.obj.message["text"] == "Войти 🔓" or event.obj.message["text"] == "/sign_in":
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        message="Введите логин:")
                    state_dict[event.obj.message['from_id']]["en_login"] = 1

                elif state_dict[event.obj.message['from_id']]["en_login"] == 1:
                    login = event.obj.message["text"]
                    with con:
                        data = con.execute(f"SELECT EXISTS (SELECT id FROM USERS WHERE login = '{login}')").fetchone()[
                            0]
                    if data:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            message="Введите пароль:")
                        state_dict[event.obj.message['from_id']]["en_login"] = 0
                        state_dict[event.obj.message['from_id']]["en_password"] = 1
                    else:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            message="Такой логин не существует, попробуйте снова:")
                        en_login = 1

                elif state_dict[event.obj.message['from_id']]["en_password"] == 1:
                    password = event.obj.message["text"]
                    with con:
                        data = con.execute(
                            f"SELECT EXISTS (SELECT id FROM USERS WHERE login = '{login}' AND password = '{password}')").fetchone()[
                            0]
                    if data:
                        with con:
                            con.execute(
                                f"UPDATE USERS SET vk_id = '{event.obj.message['from_id']}' WHERE login = '{login}'")
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=lobby_keyboard.get_keyboard(),
                            message="Успешно!")
                        state_dict[event.obj.message['from_id']]["en_password"] = 0
                        list_of_data[event.obj.message['from_id']] = []
                    else:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            message="Неправильный пароль, попробуйте снова:")
                        state_dict[event.obj.message['from_id']]["en_password"] = 1

                elif event.obj.message["text"] == "Выйти" or event.obj.message["text"] == "/sign_out":
                    with con:
                        con.execute(
                            f"UPDATE USERS SET vk_id = NULL WHERE tg_id = '{event.obj.message['from_id']}'").fetchall()
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=enter_keyboard.get_keyboard(),
                        message="Вы вышли из учётной записи.")

                elif event.obj.message["text"] == "Меню 📖" or event.obj.message["text"] == "/menu":
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj.message['from_id'],
                        keyboard=cats_keyboard.get_keyboard(),
                        message="Категории:")

                elif event.obj.message["text"] == "Корзина 🛒" or event.obj.message["text"] == "/cart":
                    with con:
                        data = con.execute(
                            f"SELECT EXISTS(SELECT id FROM USERS WHERE vk_id = '{event.obj.message['from_id']}')").fetchone()[
                            0]
                    if data:
                        with con:
                            data = con.execute("SELECT EXISTS (SELECT 1 FROM CART)").fetchone()[0]
                        if not data:
                            vk.messages.send(
                                user_id=event.obj.message['from_id'],
                                random_id=get_random_id(),
                                peer_id=event.obj.message['from_id'],
                                message="В вашей корзине пока пусто 😔")
                        else:
                            with con:
                                data = con.execute("SELECT * FROM CART").fetchall()
                            for x in data:
                                with con:
                                    name = con.execute(f"SELECT name FROM GOODS WHERE id = {x[1]}").fetchone()
                                vk.messages.send(
                                    user_id=event.obj.message['from_id'],
                                    random_id=get_random_id(),
                                    peer_id=event.obj.message['from_id'],
                                    keyboard=cart(x).get_keyboard(),
                                    message=name)
                            vk.messages.send(
                                user_id=event.obj.message['from_id'],
                                random_id=get_random_id(),
                                peer_id=event.obj.message['from_id'],
                                keyboard=order_key.get_keyboard(),
                                message="Оформить!")
                    else:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=enter_keyboard.get_keyboard(),
                            message="Для просмотра корзины необходимо войти в существующий аккаунт.")

                elif event.obj.message["text"] == "Мои заказы 📒" or event.obj.message["text"] == "/orders":
                    with con:
                        user_id = \
                            con.execute(
                                f"SELECT id FROM USERS WHERE vk_id = '{event.obj.message['from_id']}'").fetchone()[0]
                    if user_id:
                        with con:
                            data = con.execute(f"SELECT * FROM ORDERS WHERE user_id = {user_id}").fetchall()
                        if data:
                            for x in data:
                                with con:
                                    status = con.execute(f"SELECT name FROM STATUSES WHERE id = {x[3]}").fetchone()[0]
                                vk.messages.send(
                                    user_id=event.obj.message['from_id'],
                                    random_id=get_random_id(),
                                    peer_id=event.obj.message['from_id'],
                                    message=f"Заказ №{x[0]}. Время заказа: {x[2]}. Статус заказа: {status}.")
                        else:
                            vk.messages.send(
                                user_id=event.obj.message['from_id'],
                                random_id=get_random_id(),
                                peer_id=event.obj.message['from_id'],
                                message="Ваша история заказов пока что пуста 😔")
                    else:
                        vk.messages.send(
                            user_id=event.obj.message['from_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj.message['from_id'],
                            keyboard=enter_keyboard.get_keyboard(),
                            message="Для просмотра заказов необходимо войти в существующий аккаунт.")

                elif state_dict[event.obj.message['from_id']]["or_address"] == 1:
                    address = event.obj.message["text"]
                    with con:
                        con.execute(
                            f"UPDATE USERS SET last_address = '{address}' WHERE id = {event.obj.message['from_id']}")

                elif state_dict[event.obj.message['from_id']]["or_tel"] == 1:
                    tel = event.obj.message["text"]
                    with con:
                        con.execute(f"UPDATE USERS SET tel = '{tel}' WHERE id = {event.obj.message['from_id']}")



    elif event.type == VkBotEventType.MESSAGE_EVENT:
        if event.object.payload.get("type")[0] == "c":
            with con:
                list_of_data[event.obj['user_id']] = con.execute(
                    f"SELECT * FROM GOODS WHERE category = {event.object.payload.get('type')[1:]}").fetchall()
            upload = VkUpload(vk)
            photo = upload.photo_messages(f"images/{list_of_data[event.obj['user_id']][0][0]}.jpg")
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            access_key = photo[0]['access_key']
            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
            last_id = vk.messages.send(
                user_id=event.obj['user_id'],
                random_id=get_random_id(),
                peer_id=event.obj['user_id'],
                keyboard=good_page(list_of_data[event.obj['user_id']], 0).get_keyboard(),
                attachment=attachment,
                message=f"{list_of_data[event.obj['user_id']][0][1]} 🍽\n{list_of_data[event.obj['user_id']][0][3]}\n{list_of_data[event.obj['user_id']][0][2]} руб.")
        elif event.object.payload.get("type")[0] == "s":
            n = int(event.object.payload.get("type")[1:])
            upload = VkUpload(vk)
            photo = upload.photo_messages(f"images/{list_of_data[event.obj['user_id']][n][0]}.jpg")
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            access_key = photo[0]['access_key']
            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
            last_id = vk.messages.edit(
                peer_id=event.obj['user_id'],
                keyboard=good_page(list_of_data[event.obj['user_id']], n).get_keyboard(),
                conversation_message_id=event.obj.conversation_message_id,
                attachment=attachment,
                message=f"{list_of_data[event.obj['user_id']][n][1]} 🍽\n{list_of_data[event.obj['user_id']][n][3]}\n{list_of_data[event.obj['user_id']][n][2]} руб.")
        elif event.object.payload.get("type")[0] == "+":
            n = int(event.object.payload.get("type")[1:])
            count = int(event.object.payload.get("count"))
            upload = VkUpload(vk)
            photo = upload.photo_messages(f"images/{list_of_data[event.obj['user_id']][n][0]}.jpg")
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            access_key = photo[0]['access_key']
            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
            last_id = vk.messages.edit(
                peer_id=event.obj['user_id'],
                keyboard=good_page(list_of_data[event.obj['user_id']], n, count + 1).get_keyboard(),
                conversation_message_id=event.obj.conversation_message_id,
                attachment=attachment,
                message=f"{list_of_data[event.obj['user_id']][n][1]} 🍽\n{list_of_data[event.obj['user_id']][n][3]}\n{list_of_data[event.obj['user_id']][n][2]} руб.")
        elif event.object.payload.get("type")[0] == "-":
            n = int(event.object.payload.get("type")[1:])
            count = int(event.object.payload.get("count"))
            upload = VkUpload(vk)
            photo = upload.photo_messages(f"images/{list_of_data[event.obj['user_id']][n][0]}.jpg")
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            access_key = photo[0]['access_key']
            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
            last_id = vk.messages.edit(
                peer_id=event.obj['user_id'],
                keyboard=good_page(list_of_data[event.obj['user_id']], n, count - 1).get_keyboard(),
                conversation_message_id=event.obj.conversation_message_id,
                attachment=attachment,
                message=f"{list_of_data[event.obj['user_id']][n][1]} 🍽\n{list_of_data[event.obj['user_id']][n][3]}\n{list_of_data[event.obj['user_id']][n][2]} руб.")
        elif event.object.payload.get("type")[0] == "b" or event.object.payload.get("type")[0] == "a":
            with con:
                user_id = con.execute(f"SELECT id FROM USERS WHERE vk_id = '{event.obj['user_id']}'").fetchone()[0]
            if user_id:
                n = int(event.object.payload.get("type")[1:])
                count = int(event.object.payload.get("count"))
                good_id = list_of_data[event.obj['user_id']][n][0]
                if event.object.payload.get("type")[0] == "b":
                    last_id = vk.messages.send(
                        user_id=event.obj['user_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj['user_id'],
                        message="Ваш заказ ⬇️")
                    with con:
                        con.execute(f"DELETE FROM CART")
                        con.execute(
                            f"INSERT INTO CART (id, good_id, count, user_id) VALUES (1, {good_id}, {count}, {user_id})")
                        data = con.execute("SELECT * FROM CART").fetchall()
                    for x in data:
                        with con:
                            name = con.execute(f"SELECT name FROM GOODS WHERE id = {x[1]}").fetchone()
                        last_id = vk.messages.send(
                            user_id=event.obj['user_id'],
                            random_id=get_random_id(),
                            peer_id=event.obj['user_id'],
                            keyboard=cart(x).get_keyboard(),
                            message=name)
                    last_id = vk.messages.send(
                        user_id=event.obj['user_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj['user_id'],
                        keyboard=order_key.get_keyboard(),
                        message="Оформить!")
                elif event.object.payload.get("type")[0] == "a":
                    with con:
                        data = con.execute(f"SELECT EXISTS (SELECT id FROM CART WHERE good_id = {good_id})").fetchone()[
                            0]
                        if data:
                            con.execute(f"UPDATE CART SET count = count + {count}")
                        else:
                            con.execute(
                                f"INSERT INTO CART (good_id, count, user_id) VALUES ({good_id}, {count}, {user_id})")
            else:
                last_id = vk.messages.send(
                    user_id=event.obj['user_id'],
                    random_id=get_random_id(),
                    peer_id=event.obj['user_id'],
                    keyboard=enter_keyboard.get_keyboard(),
                    message="Чтобы сделать заказ, необходимо войти в существуюший аккаунт.")
        elif event.object.payload.get("type")[0] == "k":
            if event.object.payload.get("type")[1] == "+":
                with con:
                    data = con.execute("SELECT * FROM CART").fetchall()
                    con.execute(f"UPDATE CART SET count = count + 1 WHERE id = {event.object.payload.get('type')[2:]}")
                    x = con.execute(f"SELECT * FROM CART WHERE id = {event.object.payload.get('type')[2:]}").fetchone()
                for x in data:
                    with con:
                        name = con.execute(f"SELECT name FROM GOODS WHERE id = {x[1]}").fetchone()
                    last_id = vk.messages.edit(
                        peer_id=event.obj['user_id'],
                        keyboard=cart(x).get_keyboard(),
                        conversation_message_id=event.obj.conversation_message_id,
                        message=name)
            elif event.object.payload.get("type")[1] == "-":
                with con:
                    count = \
                        con.execute(
                            f"SELECT count FROM CART WHERE id = {event.object.payload.get('type')[2:]}").fetchone()[
                            0]
                if count > 1:
                    with con:
                        data = con.execute("SELECT * FROM CART").fetchall()
                        con.execute(
                            f"UPDATE CART SET count = count - 1 WHERE id = {event.object.payload.get('type')[2:]}")
                        x = con.execute(
                            f"SELECT * FROM CART WHERE id = {event.object.payload.get('type')[2:]}").fetchone()
                    for x in data:
                        with con:
                            name = con.execute(f"SELECT name FROM GOODS WHERE id = {x[1]}").fetchone()
                    last_id = vk.messages.edit(
                        peer_id=event.obj['user_id'],
                        keyboard=cart(x).get_keyboard(),
                        conversation_message_id=event.obj.conversation_message_id,
                        message=name)
            elif event.object.payload.get('type')[1] == "0":
                with con:
                    con.execute(f"DELETE FROM CART WHERE id = {event.object.payload.get('type')[2:]}")
                last_id = vk.messages.delete(
                    peer_id=event.obj['user_id'],
                    message_ids=event.obj.conversation_message_id,
                    delete_for_all=1,
                )
        elif event.object.payload.get('type')[0] == "o":
            now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            with con:
                data = con.execute(
                    f"SELECT * FROM CART WHERE user_id = (SELECT id FROM USERS WHERE vk_id = {event.obj['user_id']})").fetchall()
                user_id = con.execute(f"SELECT id FROM USERS WHERE vk_id = {event.obj['user_id']}").fetchone()[0]
                address = con.execute(f"SELECT last_address FROM USERS WHERE id = {user_id}").fetchone()[0]
                tel = con.execute(f"SELECT tel FROM USERS WHERE id = {user_id}").fetchone()[0]
                if address and tel:
                    con.execute(f"INSERT INTO ORDERS (user_id, date_time) VALUES ({user_id}, '{now}')")
                    con.execute(f"DELETE FROM CART WHERE user_id = {user_id}")
                    order_id = \
                        con.execute(
                            f"SELECT id FROM ORDERS WHERE user_id = {user_id} AND date_time = '{now}'").fetchone()[
                            0]
                    with open(f"orders/{order_id}.json", "w") as write_file:
                        json.dump(data, write_file)
                    last_id = vk.messages.send(
                        user_id=event.obj['user_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj['user_id'],
                        message=f"Заказ №{order_id} в обработке, ожидайте!")

                    bot.send_message(group_chat_id, f"Заказ №{order_id} ожидает подтверждения!",
                                     reply_markup=conf_order(order_id))
                elif not address:
                    last_id = vk.messages.send(
                        user_id=event.obj['user_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj['user_id'],
                        message=f"Для оформления необходимо ввести адресс доставки:")
                    state_dict[event.obj['user_id']]["or_address"] = 1
                elif not tel:
                    last_id = vk.messages.send(
                        user_id=event.obj['user_id'],
                        random_id=get_random_id(),
                        peer_id=event.obj['user_id'],
                        message=f"Для оформления необходимо ввести ваш номер телефона:")
                    state_dict[event.obj['user_id']]["or_tel"] = 1
