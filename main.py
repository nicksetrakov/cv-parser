from db import save_resumes_to_db
from parser_factory import ResumeParserFactory
from resume_types import SearchType, ExperienceLevel, PostingPeriod, City


def main():
    parser = ResumeParserFactory.get_parser("robota.ua")
    resumes = parser.parse_resumes(
        "python,django",
        search_type=SearchType.SKILLS,
        salary_from=3000,
        salary_to=30000,
        experience_levels=[
            ExperienceLevel.NO_EXPERIENCE,
            ExperienceLevel.UP_TO_1_YEAR,
        ],
        city=City.DNIPRO,
        posting_period=PostingPeriod.MONTH,
    )
    save_resumes_to_db(resumes)


if __name__ == "__main__":
    main()
