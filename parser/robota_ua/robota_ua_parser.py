import json
import logging
import os
from typing import List, Optional
from urllib.parse import quote, urlencode

from dotenv import load_dotenv
from selenium.common import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from logging_config import setup_logging
from parser.abstract_parser import AbstractResumeParser
from parser.relevance import calculate_resume_score
from parser.resume_types import (
    Resume,
    Experience,
    Education,
    Language,
)
from parser.robota_ua.utils import (
    RobotaSearchType,
    RobotaCity,
    RobotaExperienceLevel,
    RobotaPostingPeriod,
)
from parser.utils import convert_salary, convert_experience

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

setup_logging("robota_ua_parser.log")


class RobotaUaParser(AbstractResumeParser):
    BASE_URL = "https://robota.ua/candidates/"

    def __init__(self):
        super().__init__()
        self.login(email=EMAIL, password=PASSWORD)

    def __del__(self):
        self.driver.quit()

    def login(self, email, password):

        self.driver.get("https://robota.ua/auth/login")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "otp-username"))
        )
        self.driver.find_element(By.ID, "otp-username").send_keys(email)

        self.driver.find_element(
            By.XPATH, '//*[contains(@id, "santa-input-")]'
        ).send_keys(password)

        self.driver.find_element(
            By.CSS_SELECTOR,
            (
                "button.primary-large.santa-block."
                "santa-typo-regular-bold.full-width"
            ),
        ).click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.santa-pl-10.santa-hidden")
            )
        )

    def get_next_page_url(self, url: str) -> Optional[str]:
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "nav.santa-flex a")
                )
            )

            try:
                next_button = self.driver.find_element(
                    By.CSS_SELECTOR, "a.side-btn.next"
                )
                return next_button.get_attribute("href")
            except NoSuchElementException:
                pass

            pagination_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "nav.santa-flex a"
            )

            current_page = None

            for i, element in enumerate(pagination_elements):
                if "active" in element.get_attribute("class"):
                    current_page = i
                    break

            if current_page is not None and current_page + 1 < len(
                pagination_elements
            ):
                return pagination_elements[current_page + 1].get_attribute(
                    "href"
                )

        except TimeoutException:
            logging.error("Timeout waiting for pagination elements to load")
        except Exception as e:
            logging.error(
                "An error occurred while trying "
                f"to find the next page URL: {e}"
            )

        return None

    def get_element_text(
        self,
        by: By,
        value: str,
        element: Optional[WebElement] = None,
        default: Optional[str] = None,
    ) -> str:
        try:
            if element:
                return element.find_element(by, value).text

            return self.driver.find_element(by, value).text
        except (NoSuchElementException, StaleElementReferenceException):
            return default

    def parse_language(self, element: WebElement) -> Language:
        name = self.get_element_text(
            By.CSS_SELECTOR,
            "h4.santa-typo-regular-bold.santa-text-black-700.santa-mb-10",
            element=element,
        )
        level = self.get_element_text(
            By.CSS_SELECTOR,
            (
                "p.santa-typo-regular.santa-text-black-700."
                "santa-whitespace-nowrap.santa-sentence-case"
            ),
            element=element,
        )

        return Language(
            name=name,
            level=level,
        )

    def parse_experiences(self, job_element: WebElement) -> Experience:
        position = self.get_element_text(
            By.CSS_SELECTOR,
            (
                "h4.santa-typo-regular-bold.santa-text-black-700."
                "santa-sentence-case.santa-mb-20"
            ),
            element=job_element,
        )
        company_name = self.get_element_text(
            By.CSS_SELECTOR,
            "p.santa-typo-regular.santa-text-black-700",
            element=job_element,
        )
        company_type = self.get_element_text(
            By.CSS_SELECTOR,
            "p.santa-typo-secondary.santa-text-black-500",
            element=job_element,
        )

        period = self.get_element_text(
            By.CSS_SELECTOR,
            "span.santa-whitespace-nowrap",
            element=job_element,
        )
        description = self.get_element_text(
            By.XPATH,
            (
                '//*[contains(@class, "santa-pt-20")'
                ' and contains(@class, "700:santa-pt-10")'
                ' and contains(@class, "santa-typo-regular")'
                ' and contains(@class, "santa-break-words")'
                ' and contains(@class, "santa-list")]'
            ),
            element=job_element,
        )

        return Experience(
            company=company_name,
            company_type=company_type,
            position=position,
            years=convert_experience(period),
            description=description,
        )

    def parse_education(self, education: WebElement) -> Education:
        name = self.get_element_text(
            By.CSS_SELECTOR,
            "h4.santa-typo-regular-bold.santa-text-black-700.santa-mb-20",
            element=education,
        )

        type_education = self.get_element_text(
            By.CSS_SELECTOR,
            "p.santa-typo-regular.santa-text-black-700.santa-sentence-case",
            element=education,
        )

        location, year = self.get_element_text(
            By.CSS_SELECTOR,
            (
                "p.santa-typo-regular.santa-text-black-700."
                "santa-list.santa-sentence-case"
            ),
            element=education,
        ).split(", ")

        year = int(year)

        return Education(
            name=name,
            type_education=type_education,
            location=location,
            year=year,
        )

    def parse_single_resume(self, url: str) -> Optional[Resume]:
        self.driver.get(url)

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "santa-typo-h2.santa-text-black-700")
            )
        )

        try:
            full_name = self.get_element_text(
                By.CSS_SELECTOR, "h1.santa-typo-h2.santa-text-black-700"
            )

            position = self.get_element_text(
                By.CLASS_NAME,
                "santa-mt-10.santa-typo-secondary.santa-text-black-700",
            )

            experience_general = self.get_element_text(
                By.CSS_SELECTOR,
                "span.santa-text-red-500.santa-whitespace-nowrap",
            )
            experience_years = convert_experience(experience_general)

            experience = [
                self.parse_experiences(job)
                for job in self.driver.find_elements(
                    By.CSS_SELECTOR, "div.santa-mt-20.santa-mb-20"
                )
            ]

            try:
                education_section = self.driver.find_element(
                    By.XPATH,
                    (
                        "/html/body/app-root/div/alliance-cv-detail-"
                        "page/main/alliance-employer-cvdb-resume/"
                        "div/article/div/alliance-employer-cvdb-"
                        "desktop-resume-content/div/"
                        "div[1]/alliance-employer-resume-prof-"
                        "info/div/alliance-shared-ui-prof-"
                        "resume-education/section"
                    ),
                )
            except (
                NoSuchElementException,
                StaleElementReferenceException,
            ) as e:
                logging.info(f"No education section found in resume: {url}{e}")
                education_section = None

            if education_section:
                education = [
                    self.parse_education(element)
                    for element in education_section.find_elements(
                        By.CSS_SELECTOR,
                        "div.santa-mb-20",
                    )
                ]
            else:
                education = None

            language_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "div.language-item.santa-mb-20"
            )

            languages = [
                self.parse_language(element) for element in language_elements
            ]

            details = self.get_element_text(
                By.CSS_SELECTOR, "div.santa-m-0.santa-mb-20"
            )

            location = self.get_element_text(
                By.CSS_SELECTOR,
                (
                    "div.santa-flex.santa-items-start."
                    "santa-justify-start.santa-mb-10"
                ),
            )

            salary_element = self.get_element_text(
                By.CSS_SELECTOR, "p.santa-flex.santa-items-center.santa-mb-10"
            )
            salary = convert_salary(salary_element)

            return Resume(
                full_name=full_name,
                position=position,
                experience_years=experience_years,
                experience=experience,
                languages=languages,
                details=details,
                skills=None,
                salary=salary,
                location=location,
                education=education,
                url=url,
            )
        except Exception as e:
            logging.error(f"Error parsing single resume: {str(e)}")
            return None

    def parse_single_page(self, url: str) -> List[Resume]:
        self.driver.get(url)

        resumes = []

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "section.cv-card")
                )
            )

            resumes_section = self.driver.find_element(
                By.CSS_SELECTOR, "div.santa-space-y-10"
            )

            resume_links = resumes_section.find_elements(
                By.CSS_SELECTOR, "a.santa-no-underline"
            )

            resume_links = [
                resume.get_attribute("href") for resume in resume_links
            ]

            for resume_link in resume_links:

                resume = self.parse_single_resume(resume_link)

                resume.score = calculate_resume_score(resume)

                if resume:
                    resumes.append(resume)

        except Exception as e:
            logging.error(f"Error parsing page: {str(e)}")
        return resumes

    def build_url(
        self,
        position: str,
        search_type: RobotaSearchType = RobotaSearchType.SYNONYMS,
        city: RobotaCity = RobotaCity.ALL_UKRAINE,
        with_photo: bool = False,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        experience_levels: Optional[List[RobotaExperienceLevel]] = None,
        posting_period: RobotaPostingPeriod = RobotaPostingPeriod.THREE_MONTHS,
    ) -> str:

        position_url = (
            quote(position.replace(" ", "-").lower())
            if position != "all"
            else "all"
        )
        base_url = f"{self.BASE_URL}{position_url}/{city.filter}"

        params = {}

        if search_type != RobotaSearchType.SYNONYMS:
            params["searchType"] = json.dumps(search_type.filter)

        if with_photo:
            params["withPhoto"] = "true"

        if salary_from is not None or salary_to is not None:
            salary_dict = {
                "from": salary_from,
                "to": salary_to,
            }
            params["salary"] = json.dumps(salary_dict)

        if experience_levels is not None:
            params["experienceIds"] = json.dumps(
                [level.filter for level in experience_levels]
            )

        if posting_period != RobotaPostingPeriod.THREE_MONTHS:
            params["period"] = json.dumps(posting_period.filter)

        return f"{base_url}?{urlencode(params)}" if params else base_url

    def parse_resumes(
        self,
        position: str,
        search_type: RobotaSearchType = RobotaSearchType.SYNONYMS,
        city: RobotaCity = RobotaCity.ALL_UKRAINE,
        with_photo: bool = False,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        experience: Optional[List[RobotaExperienceLevel]] = None,
        public_period: RobotaPostingPeriod = RobotaPostingPeriod.THREE_MONTHS,
    ) -> List[Resume]:

        url = self.build_url(
            position,
            search_type,
            city,
            with_photo,
            salary_from,
            salary_to,
            experience,
            public_period,
        )

        resumes = self.parse_single_page(url)

        while True:
            url = self.get_next_page_url(url)

            if url:
                resumes.extend(self.parse_single_page(url))
            else:
                break

        return resumes
