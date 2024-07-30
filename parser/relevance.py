from parser.resume_types import Resume


def calculate_resume_score(resume: Resume) -> float:
    score = 0

    if resume.experience_years:
        score += min(resume.experience_years * 5, 50)

    completeness = (
        sum(
            [
                bool(resume.full_name),
                bool(resume.position),
                bool(resume.experience),
                bool(resume.education),
                bool(resume.skills),
                bool(resume.details),
            ]
        )
        / 6
        * 30
    )
    score += completeness

    if resume.skills:
        score += min(len(resume.skills), 10) * 2

    return score
