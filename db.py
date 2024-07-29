import sqlite3
from typing import List
from resume_types import Resume, Experience, Education, Language


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
            url TEXT
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
            INSERT INTO resumes (full_name, position, experience_years, skills, details, location, salary, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
