from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Language:
    name: str
    level: str


@dataclass
class Experience:
    position: str
    company: str
    company_type: str
    description: Optional[str]
    years: float


@dataclass
class Education:
    name: str
    type_education: str
    location: str
    year: int


@dataclass
class Resume:
    full_name: str
    position: str
    experience_years: Optional[float]
    experience: Optional[List[Experience]]
    education: Optional[List[Education]]
    skills: Optional[List[str]]
    details: Optional[str]
    location: Optional[str]
    salary: Optional[float]
    languages: Optional[List[Language]]
    url: str
