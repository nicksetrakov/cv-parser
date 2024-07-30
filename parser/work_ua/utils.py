import re
from typing import Optional

from parser.utils import BaseEnum


def extract_text_in_parentheses(text: str) -> Optional[str]:
    pattern = r"\((.*?)\)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None


def extract_city(text: str) -> Optional[str]:
    patterns = [
        r"Місто(?: проживання)?:\s*([^,\n]+)",
        r"Місто\s*([^\n]+)",
        r"Місто проживання:\s*([^,\n]+)",
        r"Готовий працювати:\s*[^,\n]+,\s*([^,\n]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


class WorkUaCity(BaseEnum):
    ALL_UKRAINE = ("", "Вся країна")
    REMOTE = ("remote", "Ремоут")
    DNIPRO = ("dnipro", "Дніпро")
    ODESA = ("odesa", "Одеса")
    KYIV = ("kyiv", "Київ")
    KHARKIV = ("kharkiv", "Харків")
    OTHER_COUNTRIES = ("other", "Інші країни")


class WorkUaSearchType(BaseEnum):
    DEFAULT = ("", "За замовчуванням")
    TITLE_ONLY = ("snowide=1", "Тільки у заголовку")
    SYNONYMS_ONLY = ("notitle=1", "Включно з синонімами")
    ANY_WORD = ("anyword=1", "Шукати будь-яке зі слів")


class WorkUaSalary(BaseEnum):
    AMOUNT_10000 = (2, "10000")
    AMOUNT_15000 = (3, "15000")
    AMOUNT_20000 = (4, "20000")
    AMOUNT_30000 = (5, "30000")
    AMOUNT_40000 = (6, "40000")
    AMOUNT_50000 = (7, "50000")
    AMOUNT_100000 = (8, "100000")


class WorkUaExperience(BaseEnum):
    NO_EXPERIENCE = (0, "Без досвіду")
    UP_TO_1_YEAR = (1, "До 1 року")
    FROM_1_TO_2_YEARS = (164, "Від 1 до 2 років")
    FROM_2_TO_5_YEARS = (165, "Від 2 до 5 років")
    OVER_5_YEARS = (166, "Понад 5 років")


class WorkUaPostingPeriod(BaseEnum):
    THREE_MONTHS = (None, "За 3 місяці")
    ONE_DAY = (1, "За 1 день")
    SEVEN_DAYS = (2, "За тиждень")
    THIRTY_DAYS = (3, "За 30 днів")
    ONE_YEAR = (5, "За рік")
    ALL_TIME = (6, "За весь час")
