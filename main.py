import json
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
    print(data_json)
    for file in os.listdir(r'proxy'):
        result_file = f'{file}\n'
        w = "%{http_code}"
        with open(f'proxy/{file}', 'r', encoding="utf-8") as f:
            for i in f:
                if '#' in i:
                    result_file += i
                elif i != '\n' and '#' not in i:
                    proxy_data = i.rstrip('\n').split(':')
                    proxy = Proxy(proxy_data[0], proxy_data[1], proxy_data[2], proxy_data[3])
                    curl_url = f'curl -x "http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}" ' \
                               f'-w {w} https://2ip.ru'
                    args = shlex.split(curl_url)
                    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    try:
                        stdout, stder = process.communicate(timeout=2)
                        data = codecs.decode(stdout)
                        if data == '000' or data.split('\n')[1] != '200':
                            if f'{proxy.ip}:{proxy.port}' not in data_json:
                                result_file += f'\U0000274C {i}'
                            else:
                                if data_json[f'{proxy.ip}:{proxy.port}']['count_error'] == 0:
                                    data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                                    result_file += f'\U000027A1 {i}'
                                else:
                                    data_json[f'{proxy.ip}:{proxy.port}']['count_error'] += 1
                                    result_file += f'\U0000274C {i}'
                        else:
                            if f'{proxy.ip}:{proxy.port}' not in data_json:
                                data_json[f'{proxy.ip}:{proxy.port}'] = {'date_check': datetime.datetime.now().strftime("%d.%m.%Y"),
                                                                         'time_check': datetime.datetime.now().strftime("%H:%M"),
                                                                         'login': proxy.user,
                                                                         'pass': proxy.password,
                                                                         'count_error': proxy.count_error,
                                                                         'count_rotation': proxy.count_rotation,
                                                                         'ip_out': data.split('\n')[0]}
                            else:
                                data_json[f'{proxy.ip}:{proxy.port}']['count_error'] = 0
                    except subprocess.TimeoutExpired:
                        result_file += f'\U0000274C {i}'
            if '\U0000274C' in result_file or '\U000027A1' in result_file:
                result += result_file + '\n'
    if '\U0000274C' in result:
        bot.send_message(chat_id, f"```\n{result}```", parse_mode='MarkdownV2')
        bot.send_message(chat_id, f"@anton_4ch")
    elif '\U000027A1' in result:
        bot.send_message(chat_id, f"```\n{result}```", parse_mode='MarkdownV2')
    print(data_json)
    with open('result.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data_json, indent=4))
except BaseException as f:
    bot.send_message(chat_id, f'\u2757\u2757\u2757 Script error: {f}')
