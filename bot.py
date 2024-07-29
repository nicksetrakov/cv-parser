import asyncio
import logging
import os
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
)
from dotenv import load_dotenv

from work_ua.work_ua_parser import WorkUaParser
from robota_ua.robota_ua_parser import RobotaUaParser

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

resume_router = Router()


class ResumeForm(StatesGroup):
    choosing_source = State()
    choosing_filters = State()
    parsing = State()
    choosing_sort = State()


@resume_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(ResumeForm.choosing_source)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Work.ua", callback_data="source_work")],
        [InlineKeyboardButton(text="Robota.ua", callback_data="source_robota")],
        [InlineKeyboardButton(text="Оба ресурса", callback_data="source_both")]
    ])
    await message.answer(
        "Выберите источник для парсинга резюме:",
        reply_markup=keyboard,
    )


@resume_router.callback_query(ResumeForm.choosing_source, F.data.startswith("source_"))
async def process_source(callback: CallbackQuery, state: FSMContext) -> None:
    source = callback.data.split('_')[1]
    await state.update_data(source=source)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить фильтры", callback_data="add_filters")],
        [InlineKeyboardButton(text="Начать парсинг", callback_data="start_parsing")]
    ])

    await callback.message.edit_text("Хотите добавить фильтры для поиска?", reply_markup=keyboard)
    await state.set_state(ResumeForm.choosing_filters)


@resume_router.callback_query(ResumeForm.choosing_filters, F.data == "add_filters")
async def process_filters(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("Фильтры добавлены. Начинаем парсинг...")
    await start_parsing(callback.message, state)


@resume_router.callback_query(ResumeForm.choosing_filters, F.data == "start_parsing")
async def start_parsing(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    source = data['source']

    work_resumes, robota_resumes = [], []

    if source == 'work' or source == 'both':
        work_resumes = WorkUaParser.parse_resumes("your_search_query")
    if source == 'robota' or source == 'both':
        robota_resumes = RobotaUaParser.parse_resumes("your_search_query")

    all_resumes = work_resumes + robota_resumes if source == 'both' else work_resumes or robota_resumes

    await message.edit_text(f"Найдено {len(all_resumes)} резюме. Как вы хотите их отсортировать?")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="По зарплате", callback_data="sort_salary")],
        [InlineKeyboardButton(text="По опыту работы", callback_data="sort_experience")]
    ])

    await message.answer("Выберите порядок сортировки:", reply_markup=keyboard)
    await state.set_state(ResumeForm.choosing_sort)
    await state.update_data(resumes=all_resumes)


@resume_router.callback_query(ResumeForm.choosing_sort, F.data.startswith("sort_"))
async def sort_resumes(callback: CallbackQuery, state: FSMContext) -> None:
    sort_type = callback.data.split('_')[1]
    data = await state.get_data()
    resumes = data['resumes']

    if sort_type == 'salary':
        resumes.sort(key=lambda x: x.salary or 0, reverse=True)
    elif sort_type == 'experience':
        resumes.sort(key=lambda x: x.experience_years or 0, reverse=True)

    await send_resumes(callback.message, resumes[:10])
    await state.clear()


async def send_resumes(message: Message, resumes: list) -> None:
    for resume in resumes:
        text = f"{html.bold('Имя:')} {html.quote(resume.full_name)}\n"
        text += f"{html.bold('Позиция:')} {html.quote(resume.position)}\n"
        text += f"{html.bold('Опыт:')} {resume.experience_years} лет\n"
        text += f"{html.bold('Локация:')} {html.quote(resume.location)}\n"
        if resume.salary:
            text += f"{html.bold('Зарплата:')} {resume.salary}\n"
        text += f"{html.bold('URL:')} {resume.url}\n"
        await message.answer(text=text)


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(resume_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
