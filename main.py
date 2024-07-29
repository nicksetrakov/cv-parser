from db import save_resumes_to_db
from parser_factory import ResumeParserFactory
from robota_ua.utils import (
    RobotaSearchType,
    RobotaExperienceLevel,
    RobotaPostingPeriod,
    RobotaCity,
)
from work_ua.utils import (
    WorkUaSalary,
    WorkUaPostingPeriod,
    WorkUaCity,
    WorkUaExperience,
    WorkUaSearchType,
)


def main():
    parser = ResumeParserFactory.get_parser("robota.ua")
    resumes = parser.parse_resumes(
        "python developer",
        search_type=RobotaSearchType.SYNONYMS,
        salary_from=3000,
        salary_to=30000,
        experience_levels=[
            RobotaExperienceLevel.FROM_1_TO_2_YEARS,
            RobotaExperienceLevel.FROM_2_TO_5_YEARS
        ],
        posting_period=RobotaPostingPeriod.MONTH,
        city=RobotaCity.DNIPRO
    )
    save_resumes_to_db(resumes)


if __name__ == "__main__":
    main()
