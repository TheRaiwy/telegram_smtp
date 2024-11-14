import logging
import smtplib
import aiosqlite
import socks
from urllib.parse import urlparse
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = '7894995841:AAE1I2v8T80Rhcr9elwR6SIla32YjlrgnGo'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

keyboard_builder = ReplyKeyboardBuilder()
keyboard_builder.add(KeyboardButton(text="📝 Отправить сообщение"))
keyboard_builder.add(KeyboardButton(text="📜 История отправок"))
keyboard = keyboard_builder.as_markup(resize_keyboard=True)

class EmailForm(StatesGroup):
    waiting_for_email_data = State()

async def init_db():
    async with aiosqlite.connect("history.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS send_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                smtp TEXT,
                recipient TEXT,
                subject TEXT,
                message TEXT,
                proxy TEXT,
                status TEXT
            )
        """)
        await db.commit()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! 👋 Выберите действие ниже, чтобы начать работу:",
        reply_markup=keyboard
    )

@dp.message(F.text == "📝 Отправить сообщение")
async def ask_all_info(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите данные в следующем формате:\n\n"
        "smtp_host|port|log|pass, получатель, тема, тело письма, тип_прокси://ip:port:login:password\n\n"
        "Пример: smtp.example.com|587|username|password, example@example.com, Тема письма, Привет! Это тест, socks5://192.168.1.1:1080:login:password.\n"
        "Если прокси не требуется, напишите 'нет'.\n",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(EmailForm.waiting_for_email_data)

def parse_proxy(proxy_str):
    if not proxy_str or proxy_str.lower() == 'нет':
        return None
    
    # Разбиваем строку по '://'
    proxy_parts = proxy_str.split('://')
    
    if len(proxy_parts) != 2:
        raise ValueError("Неправильный формат прокси. Используйте формат тип://ip:port:login:password")

    proxy_type = proxy_parts[0]
    proxy_info = proxy_parts[1].split(':')

    if len(proxy_info) != 4:
        raise ValueError("Неправильный формат прокси. Используйте формат ip:port:login:password")

    proxy_host = proxy_info[0]
    proxy_port = int(proxy_info[1])  # Преобразуем порт в число
    proxy_username = proxy_info[2]
    proxy_password = proxy_info[3]

    if proxy_type == "socks5":
        proxy_type_code = socks.SOCKS5
    elif proxy_type == "socks4":
        proxy_type_code = socks.SOCKS4
    elif proxy_type == "http":
        proxy_type_code = socks.HTTP
    else:
        raise ValueError("Неправильный тип прокси. Поддерживаются socks5, socks4 и http.")

    return (proxy_type_code, proxy_host, proxy_port, proxy_username, proxy_password)

@dp.message(EmailForm.waiting_for_email_data)
async def send_email(message: types.Message, state: FSMContext):
    try:
        lines = message.text.split(", ")
        smtp_data = lines[0].split("|")
        proxy_data = lines[4] if len(lines) > 4 else None
        recipient = lines[1]
        subject = lines[2]
        body = lines[3]

        smtp_host, smtp_port, smtp_user, smtp_pass = smtp_data
        proxy_settings = parse_proxy(proxy_data)

        if proxy_settings:
            proxy_type_code, proxy_host, proxy_port, proxy_username, proxy_password = proxy_settings
            socks.setdefaultproxy(
                proxy_type=proxy_type_code, 
                addr=proxy_host, 
                port=proxy_port, 
                username=proxy_username, 
                password=proxy_password
            )
            socks.wrapmodule(smtplib)

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient, msg.as_string())
            status = "✅ Успешно отправлено"

        logger.info(f"User: {message.from_user.id}, SMTP: {smtp_host}, Recipient: {recipient}, Subject: {subject}, Message: {body}, Proxy: {proxy_data}")

        async with aiosqlite.connect("history.db") as db:
            await db.execute("""
                INSERT INTO send_history (user_id, smtp, recipient, subject, message, proxy, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (message.from_user.id, f"{smtp_host}|{smtp_port}|{smtp_user}", recipient, subject, body, proxy_data, status))
            await db.commit()

        await message.answer(
            "✅ Сообщение успешно отправлено!\n\n"
            f"📧 Тема: {subject}\n"
            f"📬 Получатель: {recipient}\n"
            f"📜 Тело письма: {body}",
            reply_markup=keyboard
        )
    except Exception as e:
        status = f"❌ Ошибка: {str(e)}"
        logger.error(f"Error from user {message.from_user.id}: {e}")
        await message.answer(f"❌ Не удалось отправить сообщение. Ошибка: {str(e)}", reply_markup=keyboard)
    finally:
        await state.clear()

@dp.message(F.text == "📜 История отправок")
async def show_history(message: types.Message):
    async with aiosqlite.connect("history.db") as db:
        async with db.execute("SELECT smtp, recipient, subject, message, proxy, status FROM send_history WHERE user_id = ?", (message.from_user.id,)) as cursor:
            history = await cursor.fetchall()
            if history:
                history_text = "\n\n".join(
                    [f"📧 SMTP: {row[0]}\n🧑‍💻 Получатель: {row[1]}\n📜 Тема: {row[2]}\n📄 Сообщение: {row[3]}\n🛠 Прокси: {row[4]}\n📈 Статус: {row[5]}" for row in history]
                )
                await message.answer(f"📜 История отправок:\n\n{history_text}", reply_markup=keyboard)
            else:
                await message.answer("📜 История отправок пуста.", reply_markup=keyboard)

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())