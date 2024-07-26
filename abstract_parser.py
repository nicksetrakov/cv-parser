from abc import ABC, abstractmethod
from typing import List, Optional
from resume_types import Resume


class AbstractResumeParser(ABC):
    @abstractmethod
    def parse_resumes(self, position: str, **kwargs) -> List[Resume]:
        pass

    @staticmethod
    def filter_resumes(resumes: List[Resume], **kwargs) -> List[Resume]:
        # Реализация метода filter_resumes
        pass
