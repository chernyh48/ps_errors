import asyncio
import os
import telebot
from config import API_TOKEN
from core import check

API_TOKEN = API_TOKEN
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(func=lambda message: message.document.mime_type == 'text/plain', content_types=['document'])
def handle_docs_proxy(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        proxy = bot.download_file(file_info.file_path)
        file = 'check/' + message.document.file_name
        with open(file, 'wb') as new_file:
            new_file.write(proxy)
        bot.reply_to(message, f'start check {message.document.file_name}')
        asyncio.run(check('check/', os.listdir(r'check')))
        os.remove('check/' + message.document.file_name)
        bot.reply_to(message, f'finish check {message.document.file_name}')
    except Exception as e:
        bot.reply_to(message, e)


bot.infinity_polling()
