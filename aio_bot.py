import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# --- НАЛАШТУВАННЯ ---
TOKEN = "7732582992:AAHgA8kbwSxSYtxbfxcEpMgRgHtQzsz_Cys"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# База даних
GAMES_DB = {
    "Екшен": "Cyberpunk 2077, Elden Ring ⚔️",
    "Шутери": "S.T.A.L.K.E.R. 2, Metro Exodus ☢️",
    "РПГ": "The Witcher 3, Baldur's Gate 3 🐉"
}

# Стан для додавання гри
waiting_for_game = {}

# Головне меню (Кнопки)
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Топ ігор")
    builder.button(text="Випадкова гра")
    builder.button(text="Список ігор")
    builder.button(text="Додати гру")
    builder.adjust(2) # по 2 кнопки в ряд
    return builder.as_markup(resize_keyboard=True)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Я бот на Aiogram 🤖 Обирай гру:",
        reply_markup=main_menu()
    )

# Кнопка: Топ ігор
@dp.message(F.text == "Топ ігор")
async def show_top(message: types.Message):
    await message.answer("🔥 **Топ:**\n1. STALKER 2\n2. Elden Ring", parse_mode="Markdown")

# Кнопка: Список ігор
@dp.message(F.text == "Список ігор")
async def show_list(message: types.Message):
    genres = "\n".join([f"• {g}" for g in GAMES_DB.keys()])
    await message.answer(f"📂 **Категорії:**\n{genres}", parse_mode="Markdown")

# Кнопка: Випадкова гра
@dp.message(F.text == "Випадкова гра")
async def random_game(message: types.Message):
    genre = random.choice(list(GAMES_DB.keys()))
    await message.answer(f"🎲 {genre}: {GAMES_DB[genre]}")

# Кнопка: Додати гру (початок процесу)
@dp.message(F.text == "Додати гру")
async def add_game_start(message: types.Message):
    waiting_for_game[message.from_user.id] = True
    await message.answer("Напиши жанр та гру через двократку\nПриклад: `Гонки: NFS`", parse_mode="Markdown")

# Обробка тексту (додавання в базу або просто відповідь)
@dp.message()
async def handle_all(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in waiting_for_game:
        if ":" in message.text:
            genre, desc = message.text.split(":", 1)
            GAMES_DB[genre.strip()] = desc.strip()
            await message.answer(f"✅ Додано: {genre.strip()}")
            del waiting_for_game[user_id]
        else:
            await message.answer("Використовуй формат Жанр: Гра")
    else:
        await message.answer("Скористайся кнопками меню 👇")

# Запуск бота
async def main():
    print("Бот на Aiogram запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
