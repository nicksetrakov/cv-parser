import json
import logging
import time
from typing import List, Optional
from urllib.parse import quote, urlencode

from selenium.common import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

from abstract_parser import AbstractResumeParser
from resume_types import (
    Resume,
    SearchType,
    City,
    ExperienceLevel,
    PostingPeriod,
    convert_experience,
    Experience,
    Education,
    convert_salary,
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement


class RobotaUaParser(AbstractResumeParser):
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            service=ChromeService(), options=chrome_options
        )
        self.login(username="prikol9n@gmail.com", password="213051996zZ")

    def __del__(self):
        self.driver.quit()

    def login(self, username, password):
        self.driver.get("https://robota.ua/auth/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "otp-username"))
        )
        self.driver.find_element(By.ID, "otp-username").send_keys(username)

        self.driver.find_element(
            By.XPATH, '//*[contains(@id, "santa-input-")]'
        ).send_keys(password)

        self.driver.find_element(
            By.CSS_SELECTOR,
            "button.primary-large.santa-block.santa-typo-regular-bold.full-width",
        ).click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.santa-pl-10.santa-hidden")
            )
        )

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

    def parse_experiences(self, job_element: WebElement) -> Experience:
        position = self.get_element_text(
            By.CSS_SELECTOR,
            "h4.santa-typo-regular-bold.santa-text-black-700.santa-sentence-case.santa-mb-20",
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
                '//*[contains(@class, "santa-pt-20") and contains(@class, "700:santa-pt-10")'
                ' and contains(@class, "santa-typo-regular") and contains(@class, "santa-break-words")'
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
            "p.santa-typo-regular.santa-text-black-700.santa-list.santa-sentence-case",
            element=education,
        ).split(", ")

        year = int(year)

        return Education(
            name=name,
            type_education=type_education,
            location=location,
            year=year,
        )

    def parse_single_resume(self, url: str) -> Resume:
        self.driver.get(url)

        print("Open resume page")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "santa-typo-h2.santa-text-black-700")
            )
        )
        print("Started parsing single resume")
        try:
            full_name = self.get_element_text(
                By.CSS_SELECTOR, "h1.santa-typo-h2.santa-text-black-700"
            )
            print(full_name)
            position = self.get_element_text(
                By.CLASS_NAME,
                "santa-mt-10.santa-typo-secondary.santa-text-black-700",
            )
            print(position)
            experience_general = self.get_element_text(
                By.CSS_SELECTOR,
                "span.santa-text-red-500.santa-whitespace-nowrap",
            )
            print(experience_general)
            experience_years = convert_experience(experience_general)

            experience = [
                self.parse_experiences(job)
                for job in self.driver.find_elements(
                    By.CSS_SELECTOR, "div.santa-mt-20.santa-mb-20"
                )
            ]
            print(experience)
            try:
                education_section = self.driver.find_element(
                    By.XPATH,
                    (
                        "/html/body/app-root/div/alliance-cv-detail-page/main/alliance-employer-cvdb-resume/"
                        "div/article/div/alliance-employer-cvdb-desktop-resume-content/div/"
                        "div[1]/alliance-employer-resume-prof-info/div/alliance-shared-ui-prof-resume-education/section"
                    ),
                )
            except (
                NoSuchElementException,
                StaleElementReferenceException,
            ) as e:
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

            print(education)
            details = self.get_element_text(
                By.CSS_SELECTOR, "div.santa-m-0.santa-mb-20"
            )
            print(details)

            location = self.get_element_text(
                By.CSS_SELECTOR,
                "div.santa-flex.santa-items-start.santa-justify-start.santa-mb-10",
            )
            print(location)
            salary_element = self.get_element_text(
                By.CSS_SELECTOR, "p.santa-flex.santa-items-center.santa-mb-10"
            )
            salary = convert_salary(salary_element)

            print(salary)
            return Resume(
                full_name=full_name,
                position=position,
                experience_years=experience_years,
                experience=experience,
                details=details,
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
            print("Started parsing single page")
            resumes_section = self.driver.find_element(
                By.CSS_SELECTOR, "div.santa-space-y-10"
            )
            resume_links = resumes_section.find_elements(
                By.CSS_SELECTOR, "a.santa-no-underline"
            )
            resume_links = [
                resume.get_attribute("href") for resume in resume_links
            ]
            print(len(resume_links))
            for resume_link in resume_links:
                resume = self.parse_single_resume(resume_link)
                if resume:
                    resumes.append(resume)
                    print("added resume to resumes")
        except Exception as e:
            logging.error(f"Error parsing page: {str(e)}")
        return resumes

    def build_url(
        self,
        position: str,
        search_type: SearchType = SearchType.SYNONYMS,
        city: City = City.ALL_UKRAINE,
        with_photo: bool = False,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        experience_levels: Optional[List[ExperienceLevel]] = None,
        posting_period: PostingPeriod = PostingPeriod.THREE_MONTHS,
    ) -> str:

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
                "from": salary_from,
                "to": salary_to,
            }
            params["salary"] = json.dumps(salary_dict)

        if experience_levels is not None:
            params["experienceIds"] = json.dumps(
                [level.value for level in experience_levels]
            )

        if posting_period != PostingPeriod.THREE_MONTHS:
            params["period"] = json.dumps(posting_period.value)

        return f"{base_url}?{urlencode(params)}" if params else base_url

    def parse_resumes(
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
        url = self.build_url(
            position,
            search_type,
            city,
            with_photo,
            salary_from,
            salary_to,
            experience_levels,
            posting_period,
        )
        print(f"Parsing URL: {url}")
        return self.parse_single_page(url)
