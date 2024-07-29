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

from parser_factory import ResumeParserFactory
from robota_ua.utils import RobotaCity, RobotaSearchType, RobotaExperienceLevel, RobotaPostingPeriod
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
    choosing_platform = State()
    choosing_position = State()
    choosing_city = State()
    choosing_search_type = State()
    choosing_salary_from = State()
    choosing_salary_to = State()
    choosing_experience = State()
    choosing_publication_period = State()
    confirming_filters = State()
    parsing = State()


@resume_router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(ResumeForm.choosing_platform)
    await show_platform_options(message)


async def show_platform_options(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Work.ua", callback_data="platform_work.ua"
                ),
                InlineKeyboardButton(
                    text="Robota.ua", callback_data="platform_robota.ua"
                ),
            ]
        ]
    )
    await message.answer(
        "Виберіть платформу для парсингу резюме:", reply_markup=keyboard
    )


@resume_router.callback_query(
    ResumeForm.choosing_platform, F.data.startswith("platform_")
)
async def set_platform(callback: CallbackQuery, state: FSMContext) -> None:
    platform = callback.data.split("_")[1]
    await state.update_data(platform=platform)
    await callback.message.edit_text(f"Платформа обрана: {platform}")
    await state.set_state(ResumeForm.choosing_position)
    await callback.message.answer("Введіть позицію:")


@resume_router.message(ResumeForm.choosing_position)
async def set_position(message: Message, state: FSMContext) -> None:
    await state.update_data(position=message.text)
    await state.set_state(ResumeForm.choosing_city)
    await show_city_options(message, state)


async def show_city_options(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    platform = data.get("platform")

    if platform == "work.ua":
        city_enum = WorkUaCity

    else:
        city_enum = RobotaCity

    buttons = [
        InlineKeyboardButton(
            text=city.ukraine, callback_data=f"city_{city.ukraine}_{city.filter}"
        )
        for city in city_enum
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    )
    await message.answer("Виберіть місто:", reply_markup=keyboard)


@resume_router.callback_query(
    ResumeForm.choosing_city, F.data.startswith("city_")
)
async def set_city(callback: CallbackQuery, state: FSMContext) -> None:
    _, city_ukraine, city = callback.data.split("_")
    await state.update_data(city=city)
    await callback.message.edit_text(f"Місто обрано: {city_ukraine}")
    await state.set_state(ResumeForm.choosing_search_type)
    await show_search_type_options(callback.message, state)


async def show_search_type_options(
        message: Message, state: FSMContext
) -> None:
    data = await state.get_data()
    platform = data.get("platform")

    if platform == "work.ua":
        search_type_enum = WorkUaSearchType
    else:
        search_type_enum = RobotaSearchType

    buttons = [
        InlineKeyboardButton(
            text=f"{search_type.ukraine}",
            callback_data=f"search_type_{search_type.ukraine}_{search_type.filter}",
        )
        for search_type in search_type_enum
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    )
    await message.answer("Виберіть тип пошуку:", reply_markup=keyboard)


@resume_router.callback_query(
    ResumeForm.choosing_search_type, F.data.startswith("search_type_")
)
async def set_search_type(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    platform = data.get("platform")

    _, _, search_type_ukraine, search_type = callback.data.split("_")
    await state.update_data(search_type=search_type)
    await callback.message.edit_text(f"Тип пошуку вибраний: {search_type_ukraine}")
    await state.set_state(ResumeForm.choosing_salary_from)
    if platform == "robota.ua":
        await callback.message.answer(
            "Введіть 'від' в грн (наприклад, 1000):"
        )
    else:
        await show_salary_from_options(callback.message, state)


async def show_salary_from_options(message: Message, state: FSMContext) -> None:
    buttons = [
        InlineKeyboardButton(
            text=salary.ukraine,
            callback_data=f"from_{salary.filter}"
        )
        for salary in WorkUaSalary
    ]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    )
    await message.answer("Виберіть зарплату 'від'", reply_markup=keyboard)


@resume_router.message(ResumeForm.choosing_salary_from)
async def set_salary_from_rabota_ua(message: Message, state: FSMContext) -> None:
    salary_from = message.text
    await state.update_data(salary_from=salary_from)
    await state.set_state(ResumeForm.choosing_salary_to)

    await message.answer(
        "Введіть 'до' в грн (наприклад, 50000):"
    )


@resume_router.callback_query(ResumeForm.choosing_salary_from, F.data.startswith("from_"))
async def set_salary_from_work_ua(callback: CallbackQuery, state: FSMContext):
    salary_from = callback.data.split("_")[1]
    await state.update_data(salary_from=int(salary_from))
    await state.set_state(ResumeForm.choosing_salary_to)
    await show_salary_to_options(callback.message, state)


@resume_router.message(ResumeForm.choosing_salary_to)
async def set_salary_to_rabota_ua(message: Message, state: FSMContext) -> None:
    salary_to = message.text
    await state.update_data(salary_to=salary_to)

    await state.set_state(ResumeForm.choosing_experience)
    await show_experience_options(message, state)


async def show_salary_to_options(message: Message, state: FSMContext) -> None:
    buttons = [
        InlineKeyboardButton(
            text=salary.ukraine,
            callback_data=f"to_{salary.filter}"
        )
        for salary in WorkUaSalary
    ]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    )
    await message.answer("Виберіть зарплату 'до'", reply_markup=keyboard)


@resume_router.callback_query(ResumeForm.choosing_salary_to, F.data.startswith("to_"))
async def set_salary_from_work_ua(callback: CallbackQuery, state: FSMContext):
    salary_to = callback.data.split("_")[1]
    await state.update_data(salary_to=int(salary_to))

    await state.set_state(ResumeForm.choosing_experience)
    await show_experience_options(callback.message, state)


async def show_experience_options(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    platform = data.get("platform")

    if platform == "work.ua":
        experience_enum = WorkUaExperience
    else:
        experience_enum = RobotaExperienceLevel

    buttons = [
        InlineKeyboardButton(
            text=f"{experience.ukraine}",
            callback_data=f"experience_{experience.ukraine}_{experience.filter}",
        )
        for experience in experience_enum
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    )
    await message.answer("Виберіть рівень досвіду:", reply_markup=keyboard)


@resume_router.callback_query(
    ResumeForm.choosing_experience, F.data.startswith("experience_")
)
async def set_experience(callback: CallbackQuery, state: FSMContext) -> None:
    _, experience_ukraine, experience = callback.data.split("_")
    await state.update_data(experience=experience)
    await callback.message.edit_text(f"Досвід обраний: {experience_ukraine}")
    await state.set_state(ResumeForm.choosing_publication_period)
    await show_publication_period_options(callback.message, state)


async def show_publication_period_options(
        message: Message, state: FSMContext
) -> None:
    data = await state.get_data()
    platform = data.get("platform")

    if platform == "work.ua":
        period_enum = WorkUaPostingPeriod
    else:
        period_enum = RobotaPostingPeriod

    buttons = [
        InlineKeyboardButton(
            text=f"{period.ukraine}",
            callback_data=f"publication_period_{period.ukraine}_{period.filter}",
        )
        for period in period_enum
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    )
    await message.answer("Виберіть період публікації:", reply_markup=keyboard)


@resume_router.callback_query(
    ResumeForm.choosing_publication_period,
    F.data.startswith("publication_period_"),
)
async def set_publication_period(
    callback: CallbackQuery, state: FSMContext
) -> None:
    _, _, period_ukraine, period = callback.data.split("_")
    await state.update_data(publication_period=period)
    await callback.message.edit_text(f"Період публікації обрано: {period_ukraine}")
    await state.set_state(ResumeForm.confirming_filters)
    await show_filters_summary(callback.message, state)


async def show_filters_summary(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    filters_summary = (
        f"Платформа: {data.get('platform')}\n"
        f"Позиція: {data.get('position')}\n"
        f"Місто: {data.get('city')}\n"
        f"Тип пошуку: {data.get('search_type')}\n"
        f"Зарплата: от {data.get('salary_from')} до {data.get('salary_to')}\n"
        f"Досвід: {data.get('experience')}\n"
        f"Період публикації: {data.get('publication_period')}"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Підтвердити", callback_data="confirm_filters"
                ),
                InlineKeyboardButton(
                    text="Скасувати", callback_data="cancel_filters"
                ),
            ]
        ]
    )
    await message.answer(
        f"Будь ласка, підтвердіть фільтри:\n\n{filters_summary}",
        reply_markup=keyboard,
    )


@resume_router.callback_query(
    ResumeForm.confirming_filters, F.data == "confirm_filters"
)
async def confirm_filters(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ResumeForm.parsing)
    await callback.message.edit_text(
        "Фільтри підтверджені. Починаємо парсинг резюме..."
    )
    await parse_resumes(callback.message, state)


@resume_router.callback_query(
    ResumeForm.confirming_filters, F.data == "cancel_filters"
)
async def cancel_filters(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "Фільтри скасовано. Почніть знову з команди /start."
    )


async def parse_resumes(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    platform = data.get("platform")
    position = data.get("position")
    city = data.get("city")
    search_type = data.get("search_type")
    salary_from = data.get("salary_from")
    salary_to = data.get("salary_to")
    experience = data.get("experience")
    publication_period = data.get("publication_period")

    parser = ResumeParserFactory.get_parser(platform)
    print(
        platform, position, city, search_type, salary_from, salary_to, experience, publication_period
    )

    await state.clear()
    await message.answer("Парсинг завершено.")


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
