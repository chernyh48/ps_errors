import asyncio
import codecs
import datetime
import json
import os
import re
import telebot
from bs4 import BeautifulSoup
from loguru import logger
from config import *

API_TOKEN = API_TOKEN
bot = telebot.TeleBot(API_TOKEN)
chat_id = chat_id
chat_id_mobile = chat_id_mobile
time_rotation = time_rotation
count_error = count_error
data_json = {}
logger.add("logs/debug.log", format="{time:[YYYY.MM.DD hh:mm:ss:SSS]}[{level}] {message}",
           rotation="09:00", compression="zip")


class Proxy:
    def __init__(self, ip, port, user, password):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.count_error = 0

    def count_errors(self, lines, c=count_error):
        global data_json
        if f'{self.ip}:{self.port}:{self.user}:{self.password}' not in data_json:
            return f'\U0000274C{lines}'
        else:
            if data_json[f'{self.ip}:{self.port}:{self.user}:{self.password}']['count_error'] <= c - 2:
                data_json[f'{self.ip}:{self.port}:{self.user}:{self.password}']['count_error'] += 1
                return ''
            else:
                data_json[f'{self.ip}:{self.port}:{self.user}:{self.password}']['count_error'] += 1
                return f"\U0000274C({data_json[f'{self.ip}:{self.port}:{self.user}:{self.password}']['count_error']}){lines}"


async def body(direct, file_f):
    global data_json
    logger.info(f'{file_f} processing start')
    result_file = f'{file_f}\n'
    with open(os.path.abspath(f'{direct}/{file_f}'), 'r', encoding="utf-8") as file:
        try:
            for line in file:
                try:
                    line_no_n = line.rstrip('\n')
                    if '#' in line:
                        result_file += line
                    elif line != '\n' and '#' not in line:
                        proxy_data = line.rstrip('\n').split(':')
                        proxy = Proxy(proxy_data[0], proxy_data[1], proxy_data[2], proxy_data[3])
                        logger.info(f'Send request from: {proxy.ip}:{proxy.port}')
                        # if 'mobile' not in file_f:

                        # curl_url = f'curl --connect-timeout 7 --max-time 12 -x "http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}" ' \
                        #            f'https://wtfismyip.com/json'
                        curl_url = f'curl --connect-timeout 7 --max-time 12 -x "http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}" ' \
                                   f'https://api.myip.com'
                        # else:
                        #     curl_url = f'curl --connect-timeout 7 --max-time 12 -x "http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}" ' \
                        #                f'https://yandex.ru/internet'
                        process = await asyncio.create_subprocess_shell(curl_url, stdout=asyncio.subprocess.PIPE,
                                                                        stderr=asyncio.subprocess.PIPE)
                        stdout, stderr = await process.communicate()
                        data = codecs.decode(stdout)
                        error = re.findall(r"curl:[^\r\n]*", codecs.decode(stderr))
                        if error:
                            logger.warning(f'Error: {error}')
                            result_file += proxy.count_errors(line)
                        else:
                            # if 'mobile' not in file_f:
                            ip_out = json.loads(data)["ip"]
                            # ip_out = json.loads('{\n' + data.split('\n')[1][:-1] + '\n}')["YourFuckingIPAddress"]
                            logger.info(f'{proxy.ip}:{proxy.port} is OK!')
                            # else:
                            #     parsing = BeautifulSoup(data, 'lxml').find('h3', class_='parameter-header__title')
                            #     ip_out = parsing.find_next().text
                            #     logger.info(f'{proxy.ip}:{proxy.port} is OK!')
                            if line_no_n not in data_json or ip_out != data_json[line_no_n]['ip_out']:
                                data_json[line_no_n] = {
                                    'last_time_rotation': str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')),
                                    'count_error': 0,
                                    'ip_out': ip_out}
                            else:
                                if 'mobile' not in file_f:
                                    delta_time = datetime.datetime.now() - datetime.datetime.strptime(
                                        data_json[line_no_n]['last_time_rotation'], '%Y-%m-%d %H:%M:%S:%f')
                                    data_json[line_no_n]['count_error'] = 0
                                    if delta_time.seconds > time_rotation:
                                        logger.warning(f'No rotation 30 minutes: {proxy.ip}:{proxy.port}')
                                        result_file += f'\U000026A1({datetime.datetime.strptime(data_json[line_no_n]["last_time_rotation"], "%Y-%m-%d %H:%M:%S:%f").strftime("%H:%M")}){line}'
                                else:
                                    data_json[line_no_n]['count_error'] = 0
                except IndexError:
                    result_file += f'\u2757\u2757\u2757 Script error: INCORRECT PROXY FORMAT: {line}'
                    logger.warning('Message ERROR add to result')
        except BaseException as e:
            result_file += f'\u2757\u2757\u2757 Script error: {e, data}'
            logger.warning('Message ERROR add to result')
        return result_file


async def check(direct, files):
    with open(PATH_RESULT, 'r', encoding='utf-8') as j:
        global data_json
        data_json = json.load(j)
        logger.info('Dump loaded')
    try:
        logger.info('Script started')
        result = ''
        result_mobile = ''
        futures = [asyncio.create_task(body(direct, file)) for file in sorted(files)]
        result_files = await asyncio.gather(*futures)
        for result_file in result_files:
            if 'mobile' in result_file:
                if '\U0000274C' in result_file or '\u2757' in result_file:
                    if len(result_mobile + result_file) > 4096:
                        bot.send_message(chat_id_mobile, f"<pre>{result_mobile}</pre>", parse_mode='HTML')
                        result_mobile = result_file + '\n'
                    else:
                        result_mobile += result_file + '\n'
            else:
                if '\U0000274C' in result_file or '\U000026A1' in result_file or '\u2757' in result_file:
                    if len(result + result_file) > 4096:
                        bot.send_message(chat_id, f"<pre>{result}</pre>", parse_mode='HTML')
                        result = result_file + '\n'
                    else:
                        result += result_file + '\n'
        if result != '':
            bot.send_message(chat_id, f"<pre>{result}</pre>", parse_mode='HTML')
            logger.info('Message sent to telegram PS: Errors')
        if result_mobile != '':
            bot.send_message(chat_id_mobile, f"<pre>{result_mobile}</pre>", parse_mode='HTML')
            logger.info('Message sent to telegram PS: Errors_Mobile')
    except BaseException as e:
        bot.send_message(chat_id, f'\u2757\u2757\u2757 Script error: {e}')
        bot.send_message(chat_id_mobile, f'\u2757\u2757\u2757 Script error: {e}')
        logger.warning('Message ERROR sent to telegram')

    with open(PATH_RESULT, 'w', encoding='utf-8') as f:
        json.dump(data_json, f, indent=4)
        logger.info('Dump saved')
