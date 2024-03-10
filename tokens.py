from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll
import telebot

group_chat_id = -959200510
bot = telebot.TeleBot('6025298232:AAGoesIM_VvWi5pjHXPEZC_-11CLpjZN9xA')
GROUP_ID = '220351935'
GROUP_TOKEN = 'vk1.a.-lSk5BLyFF_XPscwyDEdZo0tEGcLvdvWWmcD0bQR4ih4_KecqFeCO3TtBVi09rYb8XzzL-Lw1IWPLytpwp1HFj5mWuYx5lfIyqvM1eUgOl3WDPwiCE-D1FEnJPhuIYEUJB7-R4XH2qdVgkPkpIC7XwL_EeEJa2q_Q5EoX5nM_9QfL0kjK4jd3IKZREBRHGypmyUzjhfq27chIMTK20yAmg'
API_VERSION = '5.120'
vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)
