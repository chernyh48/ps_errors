Скрипт оповещения о нерботающих прокси.

Устанавливаем зависмости:
pip install -r requirements.txt

Создаем каталог proxy в корне приложения.

Создаем каталог check в корне приложения.

В каталоге proxy создаем файлы с прокси.

В корне создаем файл result.json. В файл записываем пустой словарь: {}

Добавляем список прокси в файлы .txt в формате: ip:port:user:pass

добавляем в корень приложения файл config.py

Запускаем скрипт:
python main.py

Добавление бота в автозагрузку:

создаем файл демона:

sudo nano /lib/systemd/system/ps_error_bot.service

добавляем в файл параметры:

[Unit]
Description=PS_errors_bot Service
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/ps_errors/bot.py
StandardInput=tty-force

[Install]
WantedBy=multi-user.target


Каждый раз как вы вносите изменения в .service файлы вам нужно перезапустить демон.

sudo systemctl daemon-reload

Теперь включим запуск сервиса при загрузке системы, и запустим сам сервис:

sudo systemctl enable ps_error_bot.service
sudo systemctl start  ps_error_bot.service

Команды:
sudo systemctl status ps_error_bot.service #Статус бота
sudo systemctl stop dummy.service          #Для остановки Бота
sudo systemctl start dummy.service         #Для запуска Бота
sudo systemctl restart dummy.service       #Для перезапуска Бота
sudo systemctl enable ps_error_bot.service #Активация автозагрузки
sudo systemctl disable ps_error_bot.service #Деактивация автозагрузки



