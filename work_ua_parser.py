from typing import List

from abstract_parser import AbstractResumeParser
from resume_types import Resume
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WorkUaParser(AbstractResumeParser):
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        self.driver.quit()

    def parse_resumes(self, position: str, **kwargs) -> List[Resume]:
        # Реализация парсинга для work.ua
        pass
