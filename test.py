import telebot
from telethon.sync import TelegramClient
from env import *

token='6937176910:AAGFpaSxXwSXDaep8Qxlu1mx3qjGF4h5JK8'
bot = telebot.TeleBot(token)
id_channel = -1002123157145
client = TelegramClient(phone, api_id, api_hash)
client.start()


@bot.message_handler(content_types=['text'])
def commands(message):
    bot.send_message(id_channel, message.text)


bot.polling()
