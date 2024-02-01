from env import *
import telebot
from telethon.sync import TelegramClient
from datetime import datetime
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio


bot = telebot.TeleBot(token)
session_name = "NewsCollector"

group_list = []

# Создаем новый цикл событий для asyncio
loop = asyncio.new_event_loop()

# Создаем клиент Telethon внутри нового цикла событий
client = TelegramClient(session_name, api_id, api_hash, loop=loop)
client.start()

@bot.message_handler(commands=['add_group'])
def add_group(message):
    if len(group_list) >= 25:
        bot.reply_to(message, "Список групп полон. Удалите группу перед добавлением новой.")
    else:
        bot.reply_to(message, "Пожалуйста, введите ссылку на публичный телеграмм канал.")
        bot.register_next_step_handler(message, store_group)


def store_group(message):
    group_list.append(message.text)
    bot.reply_to(message, "Группа успешно добавлена.")


@bot.message_handler(commands=['delete_group'])
def delete_group(message):
    bot.reply_to(message, "Пожалуйста, введите идентификатор канала телеграмм, который необходимо удалить из списка.")
    bot.register_next_step_handler(message, remove_group)


def remove_group(message):
    group_list.remove(message.text)
    bot.reply_to(message, "Группа успешно удалена.")


@bot.message_handler(commands=['check_list'])
def check_list(message):
    if group_list:
        bot.reply_to(message, "\n".join(group_list))
    else:
        bot.reply_to(message, "Список групп пуст.")


@bot.message_handler(commands=['parse'])
def parsing(message):
    if not group_list:
        bot.reply_to(message, "Список отслеживаемых групп пустой.")
    else:
        bot.reply_to(message,
                     "Пожалуйста, введите дату и время (в формате 'дд.мм.гггг чч:мм'), с которой начать выгрузку постов.")
        bot.register_next_step_handler(message, parse_posts_sync)


def parse_posts_sync(message):
    # Используем созданный цикл событий для выполнения асинхронной функции
    asyncio.run_coroutine_threadsafe(parse_posts(message), loop)


def send_message_sync(chat_id, message):
    loop.call_soon(bot.send_message, chat_id, message)


async def parse_posts(message):
    date_time_str = message.text
    date_time_obj = datetime.strptime(date_time_str, '%d.%m.%Y %H:%M')

    for group in group_list:
        channel = await client(GetFullChannelRequest(group))
        posts = await client(GetHistoryRequest(
            peer=channel,
            limit=100,
            offset_date=datetime.timestamp(date_time_obj),
            add_offset=0,
            max_id=0,
            min_id=0,
            hash=0
        ))
        for post in posts.messages:
            loop.call_soon(send_message_sync, id_channel, post.message)

    loop.call_soon(send_message_sync, message.chat.id, "Выгрузка постов успешно завершена.")


bot.polling()
