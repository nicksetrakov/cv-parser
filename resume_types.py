from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum
import re


def parse_experience(experience_str):
    pattern = re.compile(
        r"(\d+)\s*р(ок[иів]{0,2})?\s*(\d+)?\s*м(ісяц[іів]{0,2})?"
    )

    match = pattern.search(experience_str)
    if not match:
        # Обработка случая, когда в строке только месяцы
        months_pattern = re.compile(r"(\d+)\s*м(ісяц[іів]{0,2})?")
        months_match = months_pattern.search(experience_str)
        if months_match:
            months = int(months_match.group(1))
            years = months / 12
            return round(years, 1)
        return 0

    years = int(match.group(1)) if match.group(1) else 0
    months = int(match.group(3)) if match.group(3) else 0

    total_years = years + (months / 12)

    return round(total_years, 1)


@dataclass
class Experience:
    company: str
    type_company: str
    description: str
    experience: int


@dataclass
class Education:
    name: str
    type_education: str
    year: datetime.date


@dataclass
class Resume:
    full_name: str
    position: str
    experience_years: Optional[int]
    experience: Optional[Experience]
    education: Optional[Education]
    details: str
    location: str
    salary: Optional[int]
    url: str


@dataclass
class SearchType(Enum):
    SYNONYMS = ""
    EVERYWHERE = "everywhere"
    SPECIALITY = "speciality"
    EDUCATION = "education"
    SKILLS = "skills"
    EXPERIENCE = "experience"


class City(Enum):
    ALL_UKRAINE = "ukraine"
    KYIV = "kyiv"
    DNIPRO = "dnipro"
    KHARKIV = "kharkiv"
    ZAPORIZHIA = "zaporizhia"
    ODESSA = "odessa"
    LVIV = "lviv"
    OTHER_COUNTRIES = "other_countries"


class ExperienceLevel(Enum):
    NO_EXPERIENCE = "0"
    UP_TO_1_YEAR = "1"
    FROM_1_TO_2_YEARS = "2"
    FROM_2_TO_5_YEARS = "3"
    FROM_5_TO_10_YEARS = "4"
    MORE_THAN_10_YEARS = "5"


class PostingPeriod(Enum):
    TODAY = "Today"
    THREE_DAYS = "ThreeDays"
    WEEK = "Week"
    MONTH = "Month"
    THREE_MONTHS = ""
    YEAR = "Year"
    ALL_TIME = "All"
