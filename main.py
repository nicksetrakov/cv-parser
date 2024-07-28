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
    parser = ResumeParserFactory.get_parser("work.ua")
    resumes = parser.parse_resumes(
        "python developer",
        search_type=WorkUaSearchType.DEFAULT,
        salary_from=WorkUaSalary.AMOUNT_5000,
        salary_to=WorkUaSalary.AMOUNT_50000,
        experience_levels=[
            WorkUaExperience.FROM_1_TO_2_YEARS,
        ],
        city=WorkUaCity.KYIV,
        posting_period=WorkUaPostingPeriod.THIRTY_DAYS,
        no_salary=True,
    )
    save_resumes_to_db(resumes)


if __name__ == "__main__":
    main()
