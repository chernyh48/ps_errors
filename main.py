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

    def count_errors(self, data_dict):
        if f'{self.ip}:{self.port}:{self.user}:{self.password}' not in data_dict:
            return f'\U0000274C {self.ip}:{self.port}:{self.user}:{self.password}\n', data_dict
        else:
            if data_dict[f'{self.ip}:{self.port}:{self.user}:{self.password}']['count_error'] <= 1:
                data_dict[f'{self.ip}:{self.port}:{self.user}:{self.password}']['count_error'] += 1
                return '\n', data_dict
            else:
                data_dict[f'{self.ip}:{self.port}:{self.user}:{self.password}']['count_error'] += 1
                return f"\U0000274C ({data_dict[f'{self.ip}:{self.port}:{self.user}:{self.password}']['count_error']}) {self.ip}:{self.port}:{self.user}:{self.password}\n", data_dict


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
                line = line.rstrip()
                if '#' in line:
                    result_file += line
                elif line != '\n' and '#' not in line:
                    proxy_data = line.rstrip('\n').split(':')
                    proxy = Proxy(proxy_data[0], proxy_data[1], proxy_data[2], proxy_data[3])
                    logger.info(f'Send request from: {proxy.ip}:{proxy.port}')
                    curl_url = f'curl -x "http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}" ' \
                               f'-w {w} https://wtfismyip.com/json'
                    args = shlex.split(curl_url)
                    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    try:
                        stdout, stderr = process.communicate(timeout=15)
                        data = codecs.decode(stdout)
                        error = re.findall(r"curl:[^\r\n]*", codecs.decode(stderr))
                        if data == '000':
                            logger.warning(f'Error: {error}')
                            result_def = proxy.count_errors(data_json)
                            result_file += result_def[0]
                            data_json = result_def[1]
                        else:
                            ip_out = json.loads(("\n".join(data.split("\n")[:2])[:-1] + '\n}'))["YourFuckingIPAddress"]
                            logger.info(f'{proxy.ip}:{proxy.port} is OK!')
                            if line not in data_json:
                                data_json[line] = {
                                    'last_time_rotation': str(datetime.datetime.now()),
                                    'count_error': 0,
                                    'ip_out': ip_out}
                            else:
                                if ip_out != data_json[line]['ip_out']:
                                    data_json[line] = {
                                        'last_time_rotation': str(datetime.datetime.now()),
                                        'count_error': 0,
                                        'ip_out': ip_out}
                                else:
                                    delta_time = datetime.datetime.now() - datetime.datetime.strptime(data_json[line]['last_time_rotation'],
                                                                                                      '%Y-%m-%d %H:%M:%S.%f')
                                    if delta_time.seconds > 1800:
                                        logger.warning(f'No rotation 30 minutes: {proxy.ip}:{proxy.port}')
                                        result_file += f'\U000026A1 ({data_json[line]["last_time_rotation"].strftime("%H:%M")}) {line}'

                    except subprocess.TimeoutExpired:
                        logger.warning(f'Timeout error: {proxy.ip}:{proxy.port}')
                        result_def = proxy.count_errors(data_json)
                        result_file += result_def[0]
                        data_json = result_def[1]
            if '\U0000274C' in result_file or '\U000026A1' in result_file:
                result += result_file + '\n'
    if '\U0000274C' in result or '\U000026A1' in result:
        bot.send_message(chat_id, f"<pre>{result}</pre>@anton_4ch", parse_mode='HTML')
        logger.info('Message sent to telegram')
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(data_json, f, indent=4)
        logger.info('Dump saved')
except BaseException as f:
    bot.send_message(chat_id, f'\u2757\u2757\u2757 Script error: {f}')
    logger.warning('Message ERROR sent to telegram')
