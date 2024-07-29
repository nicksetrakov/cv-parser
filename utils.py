import os
import re
from enum import Enum
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


class BaseEnum(Enum):

    @classmethod
    def get_display_value(cls, key: str) -> str:
        for item in cls:
            if item.value[0] == key:
                return item.value[1]
        return None

    @property
    def filter(self):
        return self.value[0]

    @property
    def ukraine(self):
        return self.value[1]

def get_exchange_rate(from_currency, to_currency) -> float:
    url = (
        f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
    )
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data["result"] == "success":
        return data["conversion_rates"][to_currency]
    else:
        raise Exception(f"Error fetching exchange rate: {data['error-type']}")


def convert_salary(salary_element) -> Optional[float]:
    if not salary_element:
        return None

    salary_element = salary_element.replace(" ", "")

    pattern = r"(\d+)(\$|грн)"
    match = re.search(pattern, salary_element)

    if match:
        amount = int(match.group(1))
        currency = match.group(2)

        if currency == "$":
            exchange_rate = get_exchange_rate("USD", "UAH")
            amount = round(amount * exchange_rate, 2)

        return amount

    return None


def convert_experience(experience_str: str | None) -> float:
    years_pattern = r"(\d+)\s*р(ік|оки|ок|.)"
    months_pattern = r"(\d+)\s*місяц(ь|і|яців|я|ів|яці)"

    years_match = re.search(years_pattern, experience_str)
    months_match = re.search(months_pattern, experience_str)

    years = int(years_match.group(1)) if years_match else 0
    months = int(months_match.group(1)) if months_match else 0

    total_years = years + (months / 12)
    return round(total_years, 1)
