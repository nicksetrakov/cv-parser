from dataclasses import dataclass
from enum import Enum


@dataclass
class RobotaSearchType(Enum):
    SYNONYMS = ""
    EVERYWHERE = "everywhere"
    SPECIALITY = "speciality"
    EDUCATION = "education"
    SKILLS = "skills"
    EXPERIENCE = "experience"


class RobotaCity(Enum):
    ALL_UKRAINE = "ukraine"
    KYIV = "kyiv"
    DNIPRO = "dnipro"
    KHARKIV = "kharkiv"
    ZAPORIZHIA = "zaporizhia"
    ODESSA = "odessa"
    LVIV = "lviv"
    OTHER_COUNTRIES = "other_countries"


class RobotaExperienceLevel(Enum):
    NO_EXPERIENCE = "0"
    UP_TO_1_YEAR = "1"
    FROM_1_TO_2_YEARS = "2"
    FROM_2_TO_5_YEARS = "3"
    FROM_5_TO_10_YEARS = "4"
    MORE_THAN_10_YEARS = "5"


class RobotaPostingPeriod(Enum):
    TODAY = "Today"
    THREE_DAYS = "ThreeDays"
    WEEK = "Week"
    MONTH = "Month"
    THREE_MONTHS = ""
    YEAR = "Year"
    ALL_TIME = "All"
