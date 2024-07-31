import sqlite3
from typing import List

from parser.resume_types import Resume, Experience, Education, Language


def clear_database(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM education")
    cursor.execute("DELETE FROM experiences")
    cursor.execute("DELETE FROM resumes")
    cursor.execute("DELETE FROM languages")
    conn.commit()


def create_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY,
            full_name TEXT,
            position TEXT,
            experience_years REAL,
            skills TEXT,
            details TEXT,
            location TEXT,
            salary INTEGER,
            url TEXT,
            score REAL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY,
            resume_id INTEGER,
            position TEXT,
            company TEXT,
            company_type TEXT,
            description TEXT,
            years REAL,
            FOREIGN KEY (resume_id) REFERENCES resumes (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY,
            resume_id INTEGER,
            name TEXT,
            type_education TEXT,
            location TEXT,
            year INTEGER,
            FOREIGN KEY (resume_id) REFERENCES resumes (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY,
            resume_id INTEGER,
            name TEXT,
            level TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes (id)
        )
        """
    )

    conn.commit()


def save_resumes_to_db(resumes: List[Resume], db_path: str = "resumes.db"):
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    clear_database(conn)
    cursor = conn.cursor()

    for resume in resumes:
        skills = ", ".join(resume.skills) if resume.skills else None
        cursor.execute(
            """
            INSERT INTO resumes (full_name, position, experience_years, skills, details, location, salary, url, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resume.full_name,
                resume.position,
                resume.experience_years,
                skills,
                resume.details,
                resume.location,
                resume.salary,
                resume.url,
                resume.score,
            ),
        )

        resume_id = cursor.lastrowid

        if resume.experience:
            for exp in resume.experience:
                cursor.execute(
                    """
                    INSERT INTO experiences (resume_id, position, company, company_type, description, years)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        resume_id,
                        exp.position,
                        exp.company,
                        exp.company_type,
                        exp.description,
                        exp.years,
                    ),
                )

        if resume.education:
            for edu in resume.education:
                cursor.execute(
                    """
                    INSERT INTO education (resume_id, name, type_education, location, year)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        resume_id,
                        edu.name,
                        edu.type_education,
                        edu.location,
                        edu.year,
                    ),
                )

        if resume.languages:
            for lang in resume.languages:
                cursor.execute(
                    """
                    INSERT INTO languages (resume_id, name, level)
                    VALUES (?, ?, ?)
                    """,
                    (
                        resume_id,
                        lang.name,
                        lang.level,
                    ),
                )

    conn.commit()
    conn.close()


def get_top_resumes(
    limit: int = 10, db_path: str = "resumes.db"
) -> List[Resume]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = (
        sqlite3.Row
    )  # Це дозволить нам звертатися до колонок за назвою
    cursor = conn.cursor()

    # Отримуємо основну інформацію про резюме
    cursor.execute(
        """
        SELECT * FROM resumes
        ORDER BY score DESC
        LIMIT ?
    """,
        (limit,),
    )
    resume_rows = cursor.fetchall()

    resumes = []
    for row in resume_rows:
        cursor.execute(
            "SELECT * FROM experiences WHERE resume_id = ?", (row["id"],)
        )
        experience_rows = cursor.fetchall()
        experiences = [
            Experience(
                position=exp["position"],
                company=exp["company"],
                company_type=exp["company_type"],
                description=exp["description"],
                years=exp["years"],
            )
            for exp in experience_rows
        ]

        cursor.execute(
            "SELECT * FROM education WHERE resume_id = ?", (row["id"],)
        )
        education_rows = cursor.fetchall()
        educations = [
            Education(
                name=edu["name"],
                type_education=edu["type_education"],
                location=edu["location"],
                year=edu["year"],
            )
            for edu in education_rows
        ]

        cursor.execute(
            "SELECT * FROM languages WHERE resume_id = ?", (row["id"],)
        )
        language_rows = cursor.fetchall()
        languages = [
            Language(name=lang["name"], level=lang["level"])
            for lang in language_rows
        ]

        # Створюємо об'єкт Resume
        resume = Resume(
            full_name=row["full_name"],
            position=row["position"],
            experience_years=row["experience_years"],
            skills=row["skills"].split(", ") if row["skills"] else None,
            details=row["details"],
            location=row["location"],
            salary=row["salary"],
            url=row["url"],
            score=row["score"],
            experience=experiences,
            education=educations,
            languages=languages,
        )
        resumes.append(resume)

    conn.close()
    return resumes
