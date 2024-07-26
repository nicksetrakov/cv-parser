import json
import logging
from enum import Enum
from urllib.parse import quote, urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Resume:
    title: str
    experience: Optional[int]
    skills: List[str]
    location: str
    salary: Optional[int]
    url: str


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


class ResumeParser:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=ChromeService(), options=chrome_options)

    def __del__(self):
        self.driver.quit()

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

        full_url = f"{base_url}?{urlencode(params)}"
        self.driver.get(full_url)

        resumes = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.resume-link"))
            )
            resume_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.resume-link")

            for resume in resume_elements:
                title_element = resume.find_element(By.CSS_SELECTOR, "a.link-profile")
                title = title_element.text.strip()
                url = "https://www.work.ua" + title_element.get_attribute("href")

                exp_element = resume.find_element(By.CSS_SELECTOR, "span.position-experience")
                experience_years = int(exp_element.text.split()[0]) if exp_element else None

                skills_element = resume.find_element(By.CSS_SELECTOR, "div.word-break")
                skills_list = [skill.strip() for skill in skills_element.text.split(",")] if skills_element else []

                location_element = resume.find_element(By.CSS_SELECTOR, "span.location")
                location = location_element.text.strip() if location_element else ""

                salary_element = resume.find_element(By.CSS_SELECTOR, "span.salary")
                salary = int(salary_element.text.replace(" ", "")) if salary_element else None

                resumes.append(Resume(title, experience_years, skills_list, location, salary, url))
        except Exception as e:
            logging.error(f"Error while parsing work.ua: {str(e)}")

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

        position_url = quote(position.replace(" ", "-").lower()) if position != "all" else "all"
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
            params["experienceIds"] = json.dumps([level.value for level in experience_levels])

        if posting_period != PostingPeriod.THREE_MONTHS:
            params["period"] = json.dumps(posting_period.value)

        full_url = f"{base_url}?{urlencode(params)}" if params else base_url

        self.driver.get(full_url)
        print(full_url)
        resumes = []
        try:

            resume_elements = self.driver.find_elements(By.CLASS_NAME, "cv-card.ng-star-inserted")

            for resume in resume_elements:
                title_element = resume.find_element(By.CSS_SELECTOR, "h2.resume-title")
                title = title_element.text.strip()
                url = title_element.find_element(By.CSS_SELECTOR, "a.resume-link").get_attribute("href")

                experience_element = resume.find_element(By.CSS_SELECTOR, "span.experience")
                experience_years = int(experience_element.text.split()[0]) if experience_element else None

                skills_element = resume.find_element(By.CSS_SELECTOR, "div.skills")
                skills_list = [skill.strip() for skill in skills_element.text.split(",")] if skills_element else []

                location_element = resume.find_element(By.CSS_SELECTOR, "span.location")
                location = location_element.text.strip() if location_element else ""

                salary_element = resume.find_element(By.CSS_SELECTOR, "span.salary")
                salary = int(salary_element.text.replace(" ", "")) if salary_element else None

                resumes.append(Resume(title, experience_years, skills_list, location, salary, url))
        except Exception as e:
            logging.error(f"Error while parsing robota.ua: {str(e)}")

        return resumes

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
            filtered_resumes = [r for r in filtered_resumes if r.experience and r.experience >= experience]

        if skills:
            filtered_resumes = [r for r in filtered_resumes if all(skill.lower() in [s.lower() for s in r.skills] for skill in skills)]

        if location:
            filtered_resumes = [r for r in filtered_resumes if location.lower() in r.location.lower()]

        if salary:
            filtered_resumes = [r for r in filtered_resumes if r.salary and r.salary >= salary]

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
                resumes = self.parse_work_ua(position, experience, skills, location, salary)
            elif site == "robota.ua":
                resumes = self.parse_robota_ua(position, experience, skills, location, salary)
            else:
                raise ValueError("Unsupported job site")

            return self.filter_resumes(resumes, experience, skills, location, salary)
        except Exception as e:
            logging.error(f"Error while fetching data from {site}: {str(e)}")
            return []


parser = ResumeParser()

resumes = parser.parse_robota_ua(
    "python,django",
    search_type=SearchType.SKILLS,
    salary_from=3000,
    salary_to=30000,
    experience_levels=[ExperienceLevel.NO_EXPERIENCE, ExperienceLevel.UP_TO_1_YEAR],
    posting_period=PostingPeriod.MONTH,
)

for resume in resumes:
    print(
        f"Title: {resume.title}, Experience: {resume.experience}, Skills: {resume.skills}, Location: {resume.location}, Salary: {resume.salary}, URL: {resume.url}")
