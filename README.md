# Telegram SMTP

Telegram SMTP — это простой бот для отправки писем через указанные SMTP-серверы с поддержкой использования прокси-серверов. Бот предоставляет пользователю возможность отправлять письма и просматривать историю отправок прямо в Telegram.

## Функции

- **Отправка email**: Бот запрашивает данные SMTP-сервера, получателя, тему, текст сообщения и опционально настройки прокси.
- **Просмотр истории отправок**: Пользователь может просмотреть историю всех отправленных сообщений, включая статус отправки.

## Используемые технологии

- Python и библиотека `aiogram` для управления ботом.
- `smtplib` для отправки email через SMTP.
- `socks` для настройки прокси.
- `aiosqlite` для хранения истории отправок.
- Поддержка нескольких типов прокси (socks4, socks5, http).

## Установка

### Требования

- Python 3.7 или выше.
- Telegram API токен для бота.

### Установка зависимостей

1. Склонируйте репозиторий:

   ```bash
   git clone https://github.com/theraiwy/telegram-smtp.git
   cd telegram-smtp

2.	Установите зависимости:

	```bash
 	pip install -r requirements.txt



Настройка

1.	Получите API-токен для бота у BotFather.
2.	Измените API-токен в app.py:
	```python
	API_TOKEN = 'INSERT_YOUR_TOKEN_FROM_@botfather'



Запуск бота

1.	Запустите бота командой:

	```bash
	python app.py


2.	Бот начнет работу и будет ждать сообщений от пользователей.

Использование

Команды

	•	/start - Запускает бота и отображает основное меню.
	•	📝 Отправить сообщение - Запрашивает данные для отправки email в формате:

smtp_host|port|username|password, recipient_email, subject, message_body, proxy_type://ip:port:login:password

Пример:

smtp.example.com|587|username|password, recipient@example.com, Test Subject, Привет! Это тестовое сообщение, socks5://192.168.1.1:1080:login:password

Если прокси не требуется, введите “нет”.

	•	📜 История отправок - Показывает историю отправленных сообщений, включая SMTP-сервер, получателя, тему, текст и статус.

Форматы прокси

Поддерживаются следующие типы прокси:
	•	socks5
	•	socks4
	•	http

Обработка ошибок

Если отправка не удалась, бот сообщит об ошибке. Убедитесь, что:
	•	Вы указали правильный SMTP-сервер и параметры.
	•	Прокси-сервер поддерживает указанный тип.

Примечания

	•	Для отправки через SMTP на порту 465 сервер должен поддерживать SSL. Если бот падает при использовании порта 465, попробуйте использовать порт 587, который поддерживает STARTTLS.

#### Лицензия

Этот проект распространяется под лицензией MIT.
