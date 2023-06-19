import json
from time import sleep

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


class Proxy:
    def __init__(self, ip, port, user, password):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.count_error = 0
        self.count_rotation = 0


try:
    result = ''
    with open('result.json', 'r', encoding='utf-8') as j:
        data_json = json.load(j)
    for file in sorted(os.listdir(r'proxy')):
        result_file = f'{file}\n'
        w = "%{http_code}"
        with open(f'proxy/{file}', 'r', encoding="utf-8") as f:
            for line in f:
                sleep(0.2)
                if '#' in line:
                    result_file += line
                elif line != '\n' and '#' not in line:
                    proxy_data = line.rstrip('\n').split(':')
                    proxy = Proxy(proxy_data[0], proxy_data[1], proxy_data[2], proxy_data[3])
                    curl_url = f'curl -x "http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}" ' \
                               f'-w {w} https://yandex.ru/internet'
                    print(curl_url)
                    args = shlex.split(curl_url)
                    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    try:
                        stdout, stder = process.communicate(timeout=2)
                        data = codecs.decode(stdout)
                        if data.split('\n')[-1] != '200':
                            if f'{proxy.ip}:{proxy.port}' not in data_json:
                                result_file += f'\U0000274C {line}'
                            else:
                                if data_json[f'{proxy.ip}:{proxy.port}']['count_error'] == 0:
                                    data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                                else:
                                    data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                                    result_file += f"\U0000274C({data_json[f'{proxy.ip}:{proxy.port}']['count_error']}){line}"
                        else:
                            if f'{proxy.ip}:{proxy.port}' not in data_json:
                                data_json[f'{proxy.ip}:{proxy.port}'] = {'date_check': datetime.datetime.now().strftime("%d.%m.%Y"),
                                                                         'time_check': datetime.datetime.now().strftime("%H:%M"),
                                                                         'login': proxy.user,
                                                                         'pass': proxy.password,
                                                                         'count_error': proxy.count_error,
                                                                         'count_rotation': proxy.count_rotation,
                                                                         'ip_out': 0}
                            else:
                                data_json[f'{proxy.ip}:{proxy.port}']['count_error'] = 0
                    except subprocess.TimeoutExpired:
                        if data_json[f'{proxy.ip}:{proxy.port}']['count_error'] == 0:
                            data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                        else:
                            data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                            result_file += f'\U0000274C {line} {proxy.count_error}'
            if '\U0000274C' in result_file:
                result += result_file + '\n'
    if '\U0000274C' in result:
        bot.send_message(chat_id, f"<pre>{result}</pre>@anton_4ch", parse_mode='HTML')
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(data_json, f, indent=4)
except BaseException as f:
    bot.send_message(chat_id, f'\u2757\u2757\u2757 Script error: {f}')
