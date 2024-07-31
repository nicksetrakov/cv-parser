from robota_ua.robota_ua_parser import RobotaUaParser
from work_ua.work_ua_parser import WorkUaParser


class ResumeParserFactory:
    @staticmethod
    def get_parser(site: str) -> WorkUaParser | RobotaUaParser:
        if site == "work.ua":
            return WorkUaParser()
        elif site == "robota.ua":
            return RobotaUaParser()
        else:
            raise ValueError("Unsupported job site")
