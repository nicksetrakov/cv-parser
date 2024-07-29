from dataclasses import dataclass
from enum import Enum

from utils import BaseEnum


@dataclass
class RobotaSearchType(BaseEnum):
    SYNONYMS = ("", "З урахуванням синонімів")
    EVERYWHERE = ("everywhere", "По всьому тексту")
    SPECIALITY = ("speciality", "У назві резюме")
    EDUCATION = ("education", "В освіті")
    SKILLS = ("skills", "У ключових навичках")
    EXPERIENCE = ("experience", "У досвіді роботи")


class RobotaCity(BaseEnum):
    ALL_UKRAINE = ("ukraine", "Вся країна")
    KYIV = ("kyiv", "Київ")
    DNIPRO = ("dnipro", "Дніпро")
    KHARKIV = ("kharkiv", "Харків")
    ZAPORIZHIA = ("zaporizhia", "Запоріжжя")
    ODESA = ("odessa", "Одеса")
    LVIV = ("lviv", "Львів")
    OTHER_COUNTRIES = ("other_countries", "Інші країни")


class RobotaExperienceLevel(BaseEnum):
    NO_EXPERIENCE = ("0", "Без досвіду")
    UP_TO_1_YEAR = ("1", "До 1 року")
    FROM_1_TO_2_YEARS = ("2", "Від 1 до 2 років")
    FROM_2_TO_5_YEARS = ("3", "Від 2 до 5 років")
    FROM_5_TO_10_YEARS = ("4", "Від 5 до 10 років")
    MORE_THAN_10_YEARS = ("5", "Понад 10 років")


class RobotaPostingPeriod(BaseEnum):
    TODAY = ("Today", "За сьогодні")
    THREE_DAYS = ("ThreeDays", "За 3 дні")
    WEEK = ("Week", "За тиждень")
    MONTH = ("Month", "За місяць")
    THREE_MONTHS = ("", "За 3 місяці")
    YEAR = ("Year", "За рік")
    ALL_TIME = ("All", "За весь час")
