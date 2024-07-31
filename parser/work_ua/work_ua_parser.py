import logging
from typing import List, Optional
from urllib.parse import quote, urlencode

from selenium.common import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from logging_config import setup_logging
from parser.abstract_parser import AbstractResumeParser
from parser.relevance import calculate_resume_score
from parser.resume_types import (
    Resume,
    Education,
    Experience,
    Language,
)
from parser.utils import convert_experience, convert_salary
from parser.work_ua.utils import (
    WorkUaCity,
    WorkUaSearchType,
    WorkUaSalary,
    WorkUaExperience,
    WorkUaPostingPeriod,
    extract_text_in_parentheses,
    extract_city,
)

setup_logging("work_ua_parser.log")


class WorkUaParser(AbstractResumeParser):
    BASE_URL = "https://www.work.ua/resumes"

    def get_next_page_url(self, url) -> Optional[str]:
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.link-icon")
                )
            )
            try:
                disabled_next_button = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "li.no-style.disabled.add-left-default"
                )
            except NoSuchElementException:
                disabled_next_button = None

            next_button = self.driver.find_element(
                By.CSS_SELECTOR, "a.link-icon"
            )

            if disabled_next_button is None and next_button.text == "Наступна":
                return next_button.get_attribute("href")

            return None

        except TimeoutException:
            logging.error("Timeout waiting for pagination elements to load")

            return None
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

    def parse_language(self) -> List[Language]:

        try:
            languages_heading = self.driver.find_element(
                By.XPATH, "//h2[contains(text(), 'Знання мов')]"
            )

            actions = ActionChains(self.driver)
            actions.move_to_element(languages_heading).perform()

            languages = []

            try:
                languages_list = languages_heading.find_element(
                    By.XPATH, "following-sibling::ul[1]"
                )
                language_items = languages_list.find_elements(
                    By.TAG_NAME, "li"
                )

                for item in language_items:
                    language_text = item.text
                    name, level = language_text.split(" — ")
                    languages.append(
                        Language(name=name.strip(), level=level.strip())
                    )
            except NoSuchElementException:
                try:
                    language_paragraph = languages_heading.find_element(
                        By.XPATH, "following-sibling::p[1]"
                    )
                    language_text = language_paragraph.text
                    name, level = language_text.split(" — ")
                    languages.append(
                        Language(name=name.strip(), level=level.strip())
                    )
                except NoSuchElementException:
                    logging.info("No language found")

            return languages

        except NoSuchElementException:
            logging.info("Languages section not found")
            return []

    def parse_experiences(self) -> List[Experience]:
        try:
            experience_heading = self.driver.find_element(
                By.XPATH, "//h2[contains(text(), 'Досвід роботи')]"
            )
        except NoSuchElementException:
            logging.info("Experience section not found")
            return []

        try:
            education_heading = self.driver.find_element(
                By.XPATH, "//h2[contains(text(), 'Освіта')]"
            )
        except NoSuchElementException:
            try:
                education_heading = self.driver.find_element(
                    By.XPATH,
                    (
                        "//h2[contains(text(), "
                        "'Додаткова освіта та сертифікати')]"
                    ),
                )
            except NoSuchElementException:
                try:
                    education_heading = self.driver.find_element(
                        By.XPATH, "//h2[contains(text(), 'Знання і навички')]"
                    )
                except NoSuchElementException:
                    education_heading = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "div.card.mt-0.card-indent-p.hidden-print",
                    )

        actions = ActionChains(self.driver)
        actions.move_to_element(experience_heading).perform()

        elements = []
        current_element = experience_heading

        while current_element != education_heading:
            current_element = current_element.find_element(
                By.XPATH, "following-sibling::*"
            )
            elements.append(current_element)

        experiences = []

        for element in elements[:-1]:
            if element.tag_name == "h2":
                position = element.text

            if element.get_attribute("class") == "mb-0":
                years, company_information = element.text.split("\n")

                years = convert_experience(extract_text_in_parentheses(years))

                company_information = company_information.split("(")

                company_name, company_type = (
                    company_information[0],
                    company_information[-1][:-1],
                )

                experience = Experience(
                    position=position,
                    company=company_name,
                    company_type=company_type,
                    description=None,
                    years=years,
                )

                experiences.append(experience)

            if element.get_attribute("class") == "text-default-7 mb-0":
                experience.description = element.text

        return experiences

    def parse_education(self) -> List[Education]:
        try:
            education_heading = self.driver.find_element(
                By.XPATH, "//h2[contains(text(), 'Освіта')]"
            )

            try:
                additional_education_heading = self.driver.find_element(
                    By.XPATH,
                    (
                        "//h2[contains(text(), "
                        "'Додаткова освіта та сертифікати')]"
                    ),
                )
            except NoSuchElementException:
                try:
                    additional_education_heading = self.driver.find_element(
                        By.XPATH,
                        "//h2[contains(text(), 'Знання і навички')]",
                    )
                except NoSuchElementException:
                    additional_education_heading = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "div.card.mt-0.card-indent-p.hidden-print",
                    )

            actions = ActionChains(self.driver)
            actions.move_to_element(education_heading).perform()

            elements = []
            current_element = education_heading
            while current_element != additional_education_heading:
                current_element = current_element.find_element(
                    By.XPATH, "following-sibling::*"
                )
                elements.append(current_element)

            educations = []
            for element in elements[:-1]:
                if element.tag_name == "h2":
                    institution = element.text

                if element.get_attribute("class") == "mb-0":
                    education_information, years = element.text.split("\n")
                    education_information = education_information.split(", ")

                    if len(education_information) == 2:
                        education_type, location = education_information
                    elif len(education_information) == 1:
                        education_type, location = (
                            education_information[0],
                            None,
                        )
                    else:
                        education_type, location = (
                            education_information[1],
                            education_information[-1],
                        )
                    years = int(years.split()[-3])

                    educations.append(
                        Education(
                            name=institution,
                            type_education=education_type,
                            location=location,
                            year=years,
                        )
                    )
        except (ValueError, NoSuchElementException):
            educations = []

        return educations

    def parse_single_resume(self, url: str) -> Optional[Resume]:
        self.driver.get(url)

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.mt-0.mb-0"))
        )

        try:
            full_name = self.get_element_text(By.CSS_SELECTOR, "h1.mt-0.mb-0")

            position_element = self.driver.find_elements(
                By.CSS_SELECTOR, "h2.mt-lg"
            )[0].text.split(", ")

            if len(position_element) == 2:
                position, salary = position_element
            elif len(position_element) >= 3:
                position, salary = (
                    ", ".join(position_element[:-1]),
                    position_element[-1],
                )
            else:
                position, salary = "".join(position_element), None

            salary = convert_salary(salary)

            experience = self.parse_experiences()

            experience_years = round(sum(exp.years for exp in experience), 1)

            education = self.parse_education()

            try:
                skills = self.driver.find_element(
                    By.XPATH,
                    (
                        "//div[@class='card wordwrap mt-0']//ul"
                        "[@class='list-unstyled my-0 flex flex-wrap']"
                    ),
                ).text.split("\n")

            except NoSuchElementException:
                skills = None

            languages = self.parse_language()

            details = self.get_element_text(By.ID, "addInfo")

            location = self.get_element_text(
                By.CSS_SELECTOR,
                "dl.dl-horizontal",
            )
            location = extract_city(location)

            return Resume(
                full_name=full_name,
                position=position,
                experience_years=experience_years,
                experience=experience,
                languages=languages,
                skills=skills,
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
                EC.presence_of_element_located((By.ID, "pjax-resume-list"))
            )

            resume_cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                (
                    "div.card.card-hover.card-search."
                    "resume-link.card-visited.wordwrap"
                ),
            )

            resume_links = [
                resume.find_element(By.TAG_NAME, "a").get_attribute("href")
                for resume in resume_cards
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
            city: WorkUaCity = WorkUaCity.ALL_UKRAINE,
            search_type: WorkUaSearchType = WorkUaSearchType.DEFAULT,
            salary_from: Optional[WorkUaSalary] = None,
            salary_to: Optional[WorkUaSalary] = None,
            no_salary: bool = False,
            experience: List[WorkUaExperience] = None,
            public_period: WorkUaPostingPeriod = WorkUaPostingPeriod.THREE_MONTHS,
    ) -> str:
        position_url = quote(position.replace(" ", "-").lower())

        if city == WorkUaCity.ALL_UKRAINE:
            base_url = f"{self.BASE_URL}-{position_url}/"
        else:
            base_url = f"{self.BASE_URL}-{city.filter}-{position_url}/"

        params = {}

        if search_type != WorkUaSearchType.DEFAULT:
            params.update(
                dict(item.split("=") for item in search_type.filter.split("&"))
            )

        if salary_from:
            params["salaryfrom"] = salary_from.filter
        if salary_to:
            params["salaryto"] = salary_to.filter
        if no_salary:
            params["nosalary"] = 1

        if experience:
            params["experience"] = "+".join(
                str(exp.filter) for exp in experience
            )

        if public_period != WorkUaPostingPeriod.THREE_MONTHS:

            params["period"] = public_period.filter

        if params:
            return f"{base_url}?{urlencode(params, safe='+')}"
        else:
            return base_url

    def parse_resumes(
            self,
            position: str,
            city: WorkUaCity = WorkUaCity.ALL_UKRAINE,
            search_type: WorkUaSearchType = WorkUaSearchType.DEFAULT,
            salary_from: Optional[WorkUaSalary] = None,
            salary_to: Optional[WorkUaSalary] = None,
            no_salary: bool = False,
            experience: List[WorkUaExperience] = None,
            public_period: WorkUaPostingPeriod = WorkUaPostingPeriod.THREE_MONTHS,
    ) -> List[Resume]:
        url = self.build_url(
            position,
            city,
            search_type,
            salary_from,
            salary_to,
            no_salary,
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
