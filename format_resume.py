from parser.resume_types import Resume


def format_resume(resume: Resume) -> str:
    formatted = f"Ім'я: {resume.full_name}\n"
    formatted += f"Позиція: {resume.position}\n"
    formatted += f"Досвід: {resume.experience_years} років\n"
    if resume.experience:
        formatted += "Опис досвіду:\n"
        for experience in resume.experience:
            formatted += f"     Позиція: {experience.position}\n"
            formatted += f"     Назва Компанії: {experience.company}\n"
            formatted += f"     Тип Компанії: {experience.company_type}\n"
            formatted += f"     Роки: {experience.years}\n\n"

    if resume.education:
        formatted += "Опис навчання:\n"
        for education in resume.education:
            formatted += f"     Назва закладу: {education.name}\n"
            formatted += f"     Тип навчання: {education.type_education}\n"
            formatted += f"     Місто: {education.location}\n"
            formatted += f"     Рік закінчення: {education.year}\n\n"

    formatted += f"Місто: {resume.location}\n"
    if resume.salary:
        formatted += f"Зарплата: {resume.salary}\n"

    if resume.skills:
        formatted += f"Навички: {', '.join(resume.skills)}\n"

    if resume.languages:
        formatted += "Знання мов:\n"
        for language in resume.languages:
            formatted += f"     Мова: {language.name}\n"
            formatted += f"     Рівень: {language.level}\n\n"

    formatted += f"URL: {resume.url}\n"
    return formatted
