import telebot
from telethon.sync import TelegramClient
from env import *

bot = telebot.TeleBot(token)
session_name = "NewsCollector"
client = TelegramClient(session_name, api_id, api_hash)
client.start()


@bot.message_handler(content_types=['text'])
def commands(message):
    bot.send_message(id_channel, message.text)


bot.polling()
