import asyncio
import random
import logging
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import BotCommand

# --- НАЛАШТУВАННЯ ---
TOKEN = "7732582992:AAHgA8kbwSxSYtxbfxcEpMgRgHtQzsz_Cys"
ADMIN_PASSWORD = "1234" 
FOLDER_NAME = "мої ігри"
FILE_NAME = "my_games.json"
DATA_PATH = os.path.join(FOLDER_NAME, FILE_NAME)

# --- РОБОТА З ДАНИМИ ---
def load_data():
    if not os.path.exists(FOLDER_NAME):
        os.makedirs(FOLDER_NAME)
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"Екшен": "Cyberpunk 2077", "Шутери": "S.T.A.L.K.E.R. 2"}

def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ІНІЦІАЛІЗАЦІЯ ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

GAMES_DB = load_data()
authorized_users = set()
waiting_for_game = {}

# --- ФУНКЦІЯ РЕЄСТРАЦІЇ КОМАНД У ТЕЛЕГРАМІ ---
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустити бота / Рестарт"),
        BotCommand(command="help", description="Допомога"),
        BotCommand(command="weather", description="Погода для геймінгу")
    ]
    await bot.set_my_commands(commands)

# --- КЛАВІАТУРА ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Топ ігор")
    builder.button(text="Випадкова гра")
    builder.button(text="Список ігор")
    builder.button(text="Додати гру")
    builder.button(text="Погода для геймінгу ☁️")
    builder.button(text="Допомога")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# --- ОБРОБНИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id in authorized_users:
        authorized_users.remove(message.from_user.id)
    await message.answer("🔒 Доступ обмежено. Введіть пароль:", reply_markup=types.ReplyKeyboardRemove())

@dp.message(Command("weather"))
@dp.message(F.text == "Погода для геймінгу ☁️")
async def cmd_weather(message: types.Message):
    weathers = [
        "Сьогодні ідеальний дощ для Silent Hill 🌧️",
        "Ясно! Краще заштор вікна, щоб не блікував монітор ☀️",
        "Туманно... Схоже на околиці Прип'яті ☢️",
        "Хмарно — ідеально для стабільного FPS ☁️"
    ]
    await message.answer(random.choice(weathers))

@dp.message()
async def handle_all(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # 1. ПЕРЕВІРКА ПАРОЛЯ
    if user_id not in authorized_users:
        if text == ADMIN_PASSWORD:
            authorized_users.add(user_id)
            await message.answer("✅ Доступ відкрито!", reply_markup=main_menu())
        else:
            await message.answer("❌ Невірний пароль. Спробуй ще раз:")
        return

    # 2. ДОДАВАННЯ ГРИ
    if user_id in waiting_for_game:
        if ":" in text:
            genre, desc = text.split(":", 1)
            GAMES_DB[genre.strip()] = desc.strip()
            save_data(GAMES_DB)
            await message.answer(f"✅ Збережено в папку '{FOLDER_NAME}'!")
            del waiting_for_game[user_id]
        else:
            await message.answer("⚠️ Формат: Жанр: Назва")
        return

    # 3. КНОПКИ
    if text == "Топ ігор":
        await message.answer("🔥 **Топ:** S.T.A.L.K.E.R. 2, Elden Ring, BG3")
    elif text == "Випадкова гра":
        genre = random.choice(list(GAMES_DB.keys()))
        await message.answer(f"🎲 {genre}: {GAMES_DB[genre]}")
    elif text == "Список ігор":
        res = "📂 **Твої ігри:**\n\n" + "\n".join([f"🔹 {g}: {i}" for g, i in GAMES_DB.items()])
        await message.answer(res, parse_mode="Markdown")
    elif text == "Додати гру":
        waiting_for_game[user_id] = True
        await message.answer("Напиши `Жанр: Назва`:")
    elif text == "Допомога" or text == "/help":
        await message.answer("Введіть пароль 1234, щоб отримати доступ до керування іграми.")

# --- ЗАПУСК ---
async def main():
    await set_commands(bot) # Реєструємо команди в меню Телеграм
    print("🚀 Бот запущений! Команди зареєстровані.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
