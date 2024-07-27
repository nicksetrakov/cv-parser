import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import asyncio

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
API_TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Функция для получения резюме из базы данных
def get_resumes(limit=5):
    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT id, full_name, position, experience_years, location, salary
    FROM resumes
    LIMIT ?
    """,
        (limit,),
    )
    resumes = cursor.fetchall()
    conn.close()
    return resumes


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для просмотра резюме. Используй /resumes для просмотра последних резюме."
    )


@dp.message(Command("resumes"))
async def cmd_resumes(message: Message):
    resumes = get_resumes()
    if not resumes:
        await message.answer("Резюме не найдены.")
        return

    response = "Последние резюме:\n\n"
    for resume in resumes:
        response += f"{hbold('Имя:')} {resume[1]}\n"
        response += f"{hbold('Позиция:')} {resume[2]}\n"
        response += f"{hbold('Опыт:')} {resume[3]} лет\n"
        response += f"{hbold('Локация:')} {resume[4]}\n"
        if resume[5]:
            response += f"{hbold('Зарплата:')} {resume[5]}\n"
        response += "\n"

    await message.answer(response, parse_mode="HTML")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
