import json
import re
from loguru import logger
import telebot
import codecs
import shlex
import subprocess
from config import *
import os
import datetime

API_TOKEN = API_TOKEN
bot = telebot.TeleBot(API_TOKEN)
chat_id = chat_id

logger.add("logs/debug.log", format="{time:[YYYY.MM.DD hh:mm:ss:SSS]}[{level}] {message}",
           rotation="09:00", compression="zip")


class Proxy:
    def __init__(self, ip, port, user, password):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.count_error = 0
        self.count_rotation = 0


try:
    logger.info('Script started')
    result = ''
    with open('result.json', 'r', encoding='utf-8') as j:
        data_json = json.load(j)
        logger.info('Dump loaded')
    for file in sorted(os.listdir(r'proxy')):
        logger.info(f'{file} processing start')
        result_file = f'{file}\n'
        w = "%{http_code}"
        with open(f'proxy/{file}', 'r', encoding="utf-8") as f:
            for line in f:
                if '#' in line:
                    result_file += line
                elif line != '\n' and '#' not in line:
                    proxy_data = line.rstrip('\n').split(':')
                    proxy = Proxy(proxy_data[0], proxy_data[1], proxy_data[2], proxy_data[3])
                    logger.info(f'Send request from: {proxy.ip}:{proxy.port}')
                    curl_url = f'curl -x "http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}" -w {w} https://wtfismyip.com/json'
                    args = shlex.split(curl_url)
                    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    try:

                        stdout, stderr = process.communicate(timeout=10)
                        data = codecs.decode(stdout)
                        error = re.findall(r"curl:[^\r\n]*", codecs.decode(stderr))
                        if data == '000':
                            logger.warning(f'Error: {error}')
                            if f'{proxy.ip}:{proxy.port}' not in data_json:
                                result_file += f'\U0000274C {line}'
                            else:
                                if data_json[f'{proxy.ip}:{proxy.port}']['count_error'] <= 2:
                                    data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                                else:
                                    data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                                    result_file += f"\U0000274C({data_json[f'{proxy.ip}:{proxy.port}']['count_error']}){line}"
                        else:
                            if f'{proxy.ip}:{proxy.port}' not in data_json:
                                data_json[f'{proxy.ip}:{proxy.port}'] = {
                                    'date_check': datetime.datetime.now().strftime("%d.%m.%Y"),
                                    'time_check': datetime.datetime.now().strftime("%H:%M"),
                                    'login': proxy.user,
                                    'pass': proxy.password,
                                    'count_error': proxy.count_error,
                                    'count_rotation': proxy.count_rotation,
                                    'ip_out': 0}
                            else:
                                logger.info(f'{proxy.ip}:{proxy.port} is OK!')
                                data_json[f'{proxy.ip}:{proxy.port}']['count_error'] = 0
                    except subprocess.TimeoutExpired:
                        logger.warning(f'Timeout error: {proxy.ip}:{proxy.port}')
                        if data_json[f'{proxy.ip}:{proxy.port}']['count_error'] <= 2:
                            data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                        else:
                            data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                            result_file += f"\U0000274C({data_json[f'{proxy.ip}:{proxy.port}']['count_error']}){line}"
            if '\U0000274C' in result_file:
                result += result_file + '\n'
    if '\U0000274C' in result:
        bot.send_message(chat_id, f"<pre>{result}</pre>@anton_4ch", parse_mode='HTML')
        logger.info('Message sent to telegram')
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(data_json, f, indent=4)
        logger.info('Dump saved')
except BaseException as f:
    bot.send_message(chat_id, f'\u2757\u2757\u2757 Script error: {f}')
    logger.warning('Message ERROR sent to telegram')
