import json
import logging
from typing import List, Optional
from urllib.parse import quote, urlencode

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from abstract_parser import AbstractResumeParser
from resume_types import (
    Resume,
    SearchType,
    City,
    ExperienceLevel,
    PostingPeriod,
    parse_experience,
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement


class RobotaUaParser(AbstractResumeParser):
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        self.driver.quit()

    def parse_single_resume(self, url: str) -> Resume:
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "santa-typo-h2.santa-text-black-700")
            )
        )
        print("Started parsing single resume")
        try:
            full_name = self.driver.find_element(
                By.CSS_SELECTOR, "h1.santa-typo-h2.santa-text-black-700"
            ).text
            print(full_name)
            position = self.driver.find_element(
                By.CLASS_NAME,
                "santa-mt-10.santa-typo-secondary.santa-text-black-700",
            ).text
            print(position)
            experience_general = self.driver.find_element(
                By.CSS_SELECTOR,
                "p.santa-mt-10.santa-typo-secondary.santa-text-black-700",
            )
            experience_years = parse_experience(experience_general)

            skills_element = self.driver.find_element(
                By.CSS_SELECTOR, "div.skills"
            )
            skills_list = (
                [skill.strip() for skill in skills_element.text.split(",")]
                if skills_element
                else []
            )

            location_element = self.driver.find_element(
                By.CSS_SELECTOR, "span.location"
            )
            location = (
                location_element.text.strip() if location_element else ""
            )

            salary_element = self.driver.find_element(
                By.CSS_SELECTOR, "span.salary"
            )
            salary = (
                int(salary_element.text.replace(" ", ""))
                if salary_element
                else None
            )
            print({"full_name": full_name})
            return Resume(experience_years, skills_list, location, salary, url)
        except Exception as e:
            logging.error(f"Error parsing single resume: {str(e)}")
            return None

    def parse_single_page(self, url: str) -> List[Resume]:
        self.driver.get(url)
        resumes = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "santa-no-underline.ng-star-inserted")
                )
            )
            resume_links = self.driver.find_elements(
                By.CSS_SELECTOR, "a.santa-no-underline.ng-star-inserted"
            )

            for resume_element in resume_links:
                print(resume_element.get_attribute("href"))
                resume = self.parse_single_resume(
                    resume_element.get_attribute("href")
                )
                if resume:
                    resumes.append(resume)
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
