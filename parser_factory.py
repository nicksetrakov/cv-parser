from abstract_parser import AbstractResumeParser
from work_ua_parser import WorkUaParser
from robota_ua_parser import RobotaUaParser


class ResumeParserFactory:
    @staticmethod
    def get_parser(site: str) -> WorkUaParser | RobotaUaParser:
        if site == "work.ua":
            return WorkUaParser()
        elif site == "robota.ua":
            return RobotaUaParser()
        else:
            raise ValueError("Unsupported job site")
