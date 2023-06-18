import telebot
import codecs
import shlex
import subprocess
from config import *
import os


API_TOKEN = API_TOKEN
bot = telebot.TeleBot(API_TOKEN)
chat_id = chat_id
try:
    for file in os.listdir(r'proxy'):
        result = f'{file}\n'
        w = "%{http_code}"
        with open(f'proxy/{file}', 'r', encoding="utf-8") as f:
            for i in f:
                if '#' in i:
                    result += i
                elif i != '\n' and '#' not in i:
                    proxy = i.rstrip('\n').split(':')
                    curl_url = f'curl -x "http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}" -w {w} https://2ip.ru'
                    args = shlex.split(curl_url)
                    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    try:
                        stdout, stder = process.communicate(timeout=2)
                        data = codecs.decode(stdout)
                        if data == '000':
                            result += f'\U0000274C {i}'
                    except subprocess.TimeoutExpired:
                        result += f'\U0000274C {i}'
            if '\U0000274C' in result:
                bot.send_message(chat_id, f"```\n{result}```", parse_mode='MarkdownV2')
except BaseException as f:
    bot.send_message(chat_id, f'\u2757\u2757\u2757 Scrypt error: {f}')
