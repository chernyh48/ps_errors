import telebot
import codecs
import shlex
import subprocess


API_TOKEN = '6218362175:AAEdq9dM10yePoTtK0mrns6HD2kbTP7x4P4'
bot = telebot.TeleBot(API_TOKEN)
chat_id = '-1001942641270'

w = "%{http_code}"
with open('proxy.txt', 'r') as f:
    proxys = f.readlines()

for i in proxys:
    proxy = i.rstrip('\n').split(':')
    curl_url = f'curl -x "http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}" -w {w} https://2ip.ru'
    args = shlex.split(curl_url)
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stder = process.communicate(timeout=2)
        data = codecs.decode(stdout)
        if data == '000':
            bot.send_message(chat_id, f'\U0000274C {i}')
    except subprocess.TimeoutExpired:
        bot.send_message(chat_id, f'\U0000274C {i}')
