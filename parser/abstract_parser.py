from abc import ABC, abstractmethod
from typing import List, Optional

from selenium import webdriver
from selenium.common import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from parser.resume_types import Resume, Language, Experience, Education


class AbstractResumeParser(ABC):

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            service=ChromeService(), options=chrome_options
        )

    @abstractmethod
    def get_next_page_url(self, url: str) -> Optional[str]:
        pass

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

    @abstractmethod
    def parse_language(self, *args) -> Language:
        pass

    @abstractmethod
    def parse_experiences(self, *args) -> Experience:
        pass

    @abstractmethod
    def parse_education(self, *args) -> Education:
        pass

    @abstractmethod
    def parse_single_resume(self, url: str) -> Optional[Resume]:
        pass

    @abstractmethod
    def parse_single_page(self, url: str) -> List[Resume]:
        pass

    @abstractmethod
    def parse_resumes(self, position: str, **kwargs) -> List[Resume]:
        pass

    @abstractmethod
    def build_url(self, **kwargs) -> str:
        pass
