from parser.resume_types import Resume


def calculate_resume_score(resume: Resume) -> float:
    """
    Calculate a score for a resume based on work experience,
    completeness, and skills.

    The score is determined by the following criteria:
    1. Work experience: 5 points per year of experience,
    up to a maximum of 50 points.
    2. Completeness of the resume: Up to 30 points based
    on the presence of key fields
       (full name, position, experience, education, skills, details).
       Each present field adds 1/6th of 30 points.
    3. Skills: 2 points per skill, up to a maximum of 10 skills
    (20 points max).

    Parameters:
    resume (Resume): The resume object to score.

    Returns:
    float: The calculated score for the resume.
    """

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
