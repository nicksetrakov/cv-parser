import json
import logging
from enum import Enum
from urllib.parse import quote, urlencode

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional

from requests import RequestException


@dataclass
class Resume:
    title: str
    experience: Optional[int]
    skills: List[str]
    location: str
    salary: Optional[int]
    url: str


class SearchType(Enum):
    SYNONYMS = ""  # З урахуванням синонімів
    EVERYWHERE = "everywhere"  # По всьому тексту
    SPECIALITY = "speciality"  # У назві резюме
    EDUCATION = "education"  # В освіті
    SKILLS = "skills"  # У ключових навичках
    EXPERIENCE = "experience"  # У досвідві роботи


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
    THREE_MONTHS = ""  # Значение по умолчанию, не отправляется в запросе
    YEAR = "Year"
    ALL_TIME = "All"


class ResumeParser:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def parse_work_ua(
        self,
        position: str,
        experience: Optional[int] = None,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        salary: Optional[int] = None,
    ) -> List[Resume]:
        base_url = "https://www.work.ua/resumes-it/"
        params = {
            "search": position,
            "experience": experience if experience else "",
            "location": location if location else "",
        }

        response = requests.get(base_url, params=params, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        resumes = []
        for resume in soup.find_all("div", class_="resume-link"):
            title = resume.find("a", class_="link-profile").text.strip()
            url = (
                "https://www.work.ua"
                + resume.find("a", class_="link-profile")["href"]
            )

            exp = resume.find("span", class_="position-experience")
            experience_years = int(exp.text.split()[0]) if exp else None

            skills_elem = resume.find("div", class_="word-break")
            skills_list = (
                [skill.strip() for skill in skills_elem.text.split(",")]
                if skills_elem
                else []
            )

            location_elem = resume.find("span", class_="location")
            location = location_elem.text.strip() if location_elem else ""

            salary_elem = resume.find("span", class_="salary")
            salary = (
                int(salary_elem.text.replace(" ", "")) if salary_elem else None
            )

            resumes.append(
                Resume(
                    title, experience_years, skills_list, location, salary, url
                )
            )

        return resumes

    def parse_robota_ua(
        self,
        position: str,
        search_type: SearchType = SearchType.SYNONYMS,
        city: City = City.ALL_UKRAINE,
        with_photo: bool = False,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        experience_levels: Optional[List[ExperienceLevel]] = None,
        posting_period: PostingPeriod = PostingPeriod.THREE_MONTHS,
    ) -> List[Resume]:

        position_url = (
            quote(position.replace(" ", "-").lower())
            if position != "all"
            else "all"
        )
        base_url = f"https://robota.ua/candidates/{position_url}/{city.value}"

        params = {}

        if search_type != SearchType.SYNONYMS:
            params["searchType"] = json.dumps(search_type.value)

        if with_photo:
            params["withPhoto"] = "true"

        if salary_from is not None or salary_to is not None:
            salary_dict = {
                "from": salary_from if salary_from is not None else None,
                "to": salary_to if salary_to is not None else None,
            }
            params["salary"] = json.dumps(salary_dict)

        if experience_levels:
            params["experienceIds"] = json.dumps(
                [level.value for level in experience_levels]
            )

        if posting_period != PostingPeriod.THREE_MONTHS:
            params["period"] = json.dumps(posting_period.value)

        full_url = f"{base_url}?{urlencode(params)}" if params else base_url
        print(full_url)

        try:
            response = requests.get(full_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            print(soup)
            resumes = []
            # Здесь нужно найти правильный селектор для списка резюме
            for resume_element in soup.select(
                "section.cv-card.ng-star-inserted"
            ):
                print(resume_element)
                # Замените на правильный селектор
                # Извлечение данных из каждого резюме
                # Этот код нужно будет адаптировать под реальную структуру HTML
                title = resume_element.find(
                    "h2", class_="resume-title"
                ).text.strip()  # Замените на правильный селектор
                url = resume_element.find("a", class_="resume-link")[
                    "href"
                ]  # Замените на правильный селектор

                experience_elem = resume_element.find(
                    "span", class_="experience"
                )  # Замените на правильный селектор
                experience_years = (
                    self.extract_experience(experience_elem.text)
                    if experience_elem
                    else None
                )

                skills_elem = resume_element.find(
                    "div", class_="skills"
                )  # Замените на правильный селектор
                skills_list = (
                    [skill.strip() for skill in skills_elem.text.split(",")]
                    if skills_elem
                    else []
                )

                location_elem = resume_element.find(
                    "span", class_="location"
                )  # Замените на правильный селектор
                location = location_elem.text.strip() if location_elem else ""

                salary_elem = resume_element.find(
                    "span", class_="salary"
                )  # Замените на правильный селектор
                salary = (
                    self.extract_salary(salary_elem.text)
                    if salary_elem
                    else None
                )

                resumes.append(
                    Resume(
                        title,
                        experience_years,
                        skills_list,
                        location,
                        salary,
                        url,
                    )
                )

            return resumes

        except requests.RequestException as e:
            logging.error(f"Error fetching data from robota.ua: {e}")
            return []
        except Exception as e:
            logging.error(f"Error parsing data from robota.ua: {e}")
            return []

    def filter_resumes(
        self,
        resumes: List[Resume],
        experience: Optional[int] = None,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        salary: Optional[int] = None,
    ) -> List[Resume]:
        filtered_resumes = resumes

        if experience:
            filtered_resumes = [
                r
                for r in filtered_resumes
                if r.experience and r.experience >= experience
            ]

        if skills:
            filtered_resumes = [
                r
                for r in filtered_resumes
                if all(
                    skill.lower() in [s.lower() for s in r.skills]
                    for skill in skills
                )
            ]

        if location:
            filtered_resumes = [
                r
                for r in filtered_resumes
                if location.lower() in r.location.lower()
            ]

        if salary:
            filtered_resumes = [
                r for r in filtered_resumes if r.salary and r.salary >= salary
            ]

        return filtered_resumes

    def parse_resumes(
        self,
        site: str,
        position: str,
        experience: Optional[int] = None,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        salary: Optional[int] = None,
    ) -> List[Resume]:
        try:
            if site == "work.ua":
                resumes = self.parse_work_ua(
                    position, experience, skills, location, salary
                )
            elif site == "robota.ua":
                resumes = self.parse_robota_ua(
                    position, experience, skills, location, salary
                )
            else:
                raise ValueError("Unsupported job site")

            return self.filter_resumes(
                resumes, experience, skills, location, salary
            )
        except RequestException as e:
            logging.error(f"Error while fetching data from {site}: {str(e)}")
            return []
        except Exception as e:
            logging.error(
                f"Unexpected error while parsing resumes from {site}: {str(e)}"
            )
            return []


parser = ResumeParser()

parser.parse_robota_ua(
    "python,django",
    search_type=SearchType.SKILLS,
    salary_from=3000,
    salary_to=30000,
    experience_levels=[
        ExperienceLevel.NO_EXPERIENCE,
        ExperienceLevel.FROM_2_TO_5_YEARS,
    ],
    city=City.DNIPRO,
    posting_period=PostingPeriod.ALL_TIME,
)
