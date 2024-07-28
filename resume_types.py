from dataclasses import dataclass
from typing import List, Optional

import requests
import re

# Ваш API ключ
API_KEY = "f096de09457b415abbdfb0bf"


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
    # Регулярное выражение для извлечения лет и месяцев опыта
    years_pattern = r'(\d+)\s*р(ік|оки|ок|.)'
    months_pattern = r'(\d+)\s*місяц(ь|і|яців|я|ів|яці)'

    years_match = re.search(years_pattern, experience_str)
    months_match = re.search(months_pattern, experience_str)

    years = int(years_match.group(1)) if years_match else 0
    months = int(months_match.group(1)) if months_match else 0

    total_years = years + (months / 12)
    return round(total_years, 1)


@dataclass
class Language:
    name: str
    level: str


@dataclass
class Experience:
    position: str
    company: str
    company_type: str
    description: str
    years: float


@dataclass
class Education:
    name: str
    type_education: str
    location: str
    year: int


@dataclass
class Resume:
    full_name: str
    position: str
    experience_years: Optional[float]
    experience: Optional[List[Experience]]
    education: Optional[List[Education]]
    skills: Optional[List[str]]
    details: Optional[str]
    location: Optional[str]
    salary: Optional[float]
    languages: Optional[List[Language]]
    url: str
