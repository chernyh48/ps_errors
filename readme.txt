Скрипт оповещения о нерботающих прокси.

Устанавливаем зависмости:
pip install -r requirements.txt

Создаем каталог proxy в корне приложения.

В каталоге proxy создаем файлы с прокси.

В корне создаем файл result.json. В файл записываем пустой словарь: {}

Добавляем список прокси в файлы .txt в формате: ip:port:user:pass

добавляем в корень приложения файл config.py

Запускаем скрипт:
python main.py