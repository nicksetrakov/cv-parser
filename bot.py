import asyncio
import logging
import os
import sys
from os import getenv
from typing import Optional, List

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

from work_ua.work_ua_parser import (
    WorkUaParser,
    WorkUaCity,
    WorkUaSearchType,
    WorkUaSalary,
    WorkUaExperience,
    WorkUaPostingPeriod,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

resume_router = Router()


class ResumeForm(StatesGroup):
    choosing_source = State()
    choosing_filters = State()
    parsing = State()
    choosing_sort = State()
    choosing_city = State()
    choosing_search_type = State()
    choosing_salary_from = State()
    choosing_salary_to = State()
    choosing_experience = State()
    choosing_publication_period = State()


@resume_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(ResumeForm.choosing_source)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Work.ua", callback_data="source_work"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Robota.ua", callback_data="source_robota"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Оба ресурса", callback_data="source_both"
                )
            ],
        ]
    )
    await message.answer(
        "Выберите источник для парсинга резюме:",
        reply_markup=keyboard,
    )


@resume_router.callback_query(
    ResumeForm.choosing_source, F.data.startswith("source_")
)
async def process_source(callback: CallbackQuery, state: FSMContext) -> None:
    source = callback.data.split("_")[1]
    await state.update_data(source=source)

    # Устанавливаем состояние для фильтров
    await state.set_state(ResumeForm.choosing_filters)

    # Показываем фильтры
    await show_filter_options(callback.message, state)


@resume_router.callback_query(
    ResumeForm.choosing_filters, F.data.startswith("filter_")
)
async def choose_filter(callback: CallbackQuery, state: FSMContext) -> None:
    filter_type = callback.data.split("_")[1]
    if filter_type == "city":
        await show_city_options(callback.message, state)
    elif filter_type == "search_type":
        await show_search_type_options(callback.message, state)
    elif filter_type == "salary_from":
        await show_salary_from_options(callback.message, state)
    elif filter_type == "salary_to":
        await show_salary_to_options(callback.message, state)
    elif filter_type == "experience":
        await show_experience_options(callback.message, state)
    elif filter_type == "publication_period":
        await show_publication_period_options(callback.message, state)


async def show_city_options(message: Message, state: FSMContext) -> None:
    buttons = [
        InlineKeyboardButton(
            text=city.name, callback_data=f"city_{city.value}"
        )
        for city in WorkUaCity
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    )
    await message.edit_text("Выберите город:", reply_markup=keyboard)
    await state.set_state(ResumeForm.choosing_city)


@resume_router.callback_query(
    ResumeForm.choosing_city, F.data.startswith("city_")
)
async def set_city(callback: CallbackQuery, state: FSMContext) -> None:
    city = callback.data.split("_")[1]
    await state.update_data(city=city)
    await callback.message.edit_text(f"Город установлен: {city}")
    await state.set_state(ResumeForm.choosing_source)
    await process_source(callback, state)


async def show_search_type_options(
    message: Message, state: FSMContext
) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=st.name, callback_data=f"search_type_{st.value}"
                )
                for st in WorkUaSearchType
            ]
        ]
    )
    await message.edit_text("Выберите тип поиска:", reply_markup=keyboard)
    await state.set_state(ResumeForm.choosing_search_type)


@resume_router.callback_query(
    ResumeForm.choosing_search_type, F.data.startswith("search_type_")
)
async def set_search_type(callback: CallbackQuery, state: FSMContext) -> None:
    search_type = callback.data.split("_")[1]
    await state.update_data(search_type=search_type)
    await callback.message.edit_text(f"Тип поиска установлен: {search_type}")
    await show_filter_options(callback.message, state)


async def show_salary_from_options(
    message: Message, state: FSMContext
) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{salary.name}",
                    callback_data=f"salary_from_{salary.value}",
                )
                for salary in WorkUaSalary
            ]
        ]
    )
    await message.edit_text(
        "Выберите минимальную зарплату:", reply_markup=keyboard
    )
    await state.set_state(ResumeForm.choosing_salary_from)


@resume_router.callback_query(
    ResumeForm.choosing_salary_from, F.data.startswith("salary_from_")
)
async def set_salary_from(callback: CallbackQuery, state: FSMContext) -> None:
    salary_from = callback.data.split("_")[2]
    await state.update_data(salary_from=salary_from)
    await callback.message.edit_text(
        f"Минимальная зарплата установлена: {salary_from}"
    )
    await show_filter_options(callback.message, state)


async def show_salary_to_options(message: Message, state: FSMContext) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{salary.name}",
                    callback_data=f"salary_to_{salary.value}",
                )
                for salary in WorkUaSalary
            ]
        ]
    )
    await message.edit_text(
        "Выберите максимальную зарплату:", reply_markup=keyboard
    )
    await state.set_state(ResumeForm.choosing_salary_to)


@resume_router.callback_query(
    ResumeForm.choosing_salary_to, F.data.startswith("salary_to_")
)
async def set_salary_to(callback: CallbackQuery, state: FSMContext) -> None:
    salary_to = callback.data.split("_")[2]
    await state.update_data(salary_to=salary_to)
    await callback.message.edit_text(
        f"Максимальная зарплата установлена: {salary_to}"
    )
    await show_filter_options(callback.message, state)


async def show_experience_options(message: Message, state: FSMContext) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{exp.name}", callback_data=f"experience_{exp.value}"
                )
                for exp in WorkUaExperience
            ]
        ]
    )
    await message.edit_text("Выберите опыт работы:", reply_markup=keyboard)
    await state.set_state(ResumeForm.choosing_experience)


@resume_router.callback_query(
    ResumeForm.choosing_experience, F.data.startswith("experience_")
)
async def set_experience(callback: CallbackQuery, state: FSMContext) -> None:
    experience = callback.data.split("_")[1]
    await state.update_data(experience=experience)
    await callback.message.edit_text(f"Опыт работы установлен: {experience}")
    await show_filter_options(callback.message, state)


async def show_publication_period_options(
    message: Message, state: FSMContext
) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{pp.name}",
                    callback_data=f"publication_period_{pp.value}",
                )
                for pp in WorkUaPostingPeriod
            ]
        ]
    )
    await message.edit_text(
        "Выберите период публикации:", reply_markup=keyboard
    )
    await state.set_state(ResumeForm.choosing_publication_period)


@resume_router.callback_query(
    ResumeForm.choosing_publication_period,
    F.data.startswith("publication_period_"),
)
async def set_publication_period(
    callback: CallbackQuery, state: FSMContext
) -> None:
    publication_period = callback.data.split("_")[2]
    await state.update_data(publication_period=publication_period)
    await callback.message.edit_text(
        f"Период публикации установлен: {publication_period}"
    )
    await show_filter_options(callback.message, state)


async def show_filter_options(message: Message, state: FSMContext) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Город", callback_data="filter_city")],
            [
                InlineKeyboardButton(
                    text="Тип поиска", callback_data="filter_search_type"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Зарплата от", callback_data="filter_salary_from"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Зарплата до", callback_data="filter_salary_to"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Опыт работы", callback_data="filter_experience"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Период публикации",
                    callback_data="filter_publication_period",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Начать парсинг", callback_data="start_parsing"
                )
            ],
        ]
    )
    await message.edit_text(
        "Выберите фильтры для поиска или начните парсинг:",
        reply_markup=keyboard,
    )


@resume_router.callback_query(
    ResumeForm.choosing_filters, F.data == "start_parsing"
)
async def start_parsing(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    parser = WorkUaParser()
    resumes = parser.parse_resumes(
        position=data.get("position", ""),
        city=WorkUaCity[data.get("city", "ALL_UKRAINE").upper()],
        search_type=WorkUaSearchType[
            data.get("search_type", "DEFAULT").upper()
        ],
        salary_from=(
            WorkUaSalary[data.get("salary_from")]
            if data.get("salary_from")
            else None
        ),
        salary_to=(
            WorkUaSalary[data.get("salary_to")]
            if data.get("salary_to")
            else None
        ),
        no_salary=False,  # You can add a filter for this if needed
        experience_levels=(
            [WorkUaExperience[data.get("experience").upper()]]
            if data.get("experience")
            else None
        ),
        posting_period=WorkUaPostingPeriod[
            data.get("publication_period", "THREE_MONTHS").upper()
        ],
    )

    # Do something with the resumes, e.g., send a summary to the user
    resume_summaries = "\n\n".join([str(resume) for resume in resumes])
    await callback.message.edit_text(f"Найденные резюме:\n{resume_summaries}")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_router(resume_router)

    bot = Bot(
        token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp.run_polling(bot, skip_updates=True)


if __name__ == "__main__":
    main()
