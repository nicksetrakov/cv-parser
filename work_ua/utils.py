from enum import Enum


class WorkUaCity(Enum):
    ALL_UKRAINE = ""
    REMOTE = "remote"
    DNIPRO = "dnipro"
    ODESA = "odesa"
    KYIV = "kyiv"
    KHARKIV = "kharkiv"
    OTHER_COUNTRIES = "other"


class WorkUaSearchType(Enum):
    DEFAULT = ""
    TITLE_ONLY = "snowide=1"
    SYNONYMS_ONLY = "notitle=1"
    ANY_WORD = "anyword=1"


class WorkUaSalary(Enum):
    AMOUNT_5000 = 5
    AMOUNT_7000 = 7
    AMOUNT_10000 = 10
    AMOUNT_15000 = 11
    AMOUNT_20000 = 12
    AMOUNT_25000 = 13
    AMOUNT_30000 = 14
    AMOUNT_40000 = 15
    AMOUNT_50000 = 16
    AMOUNT_100000 = 17


class WorkUaExperience(Enum):
    NO_EXPERIENCE = 0
    UP_TO_1_YEAR = 1
    FROM_1_TO_2_YEARS = 164
    FROM_2_TO_5_YEARS = 165
    OVER_5_YEARS = 166


class WorkUaPostingPeriod(Enum):
    THREE_MONTHS = None
    ONE_DAY = 1
    SEVEN_DAYS = 2
    THIRTY_DAYS = 3
    ONE_YEAR = 5
    ALL_TIME = 6
