from dataclasses import dataclass
from datetime import date


@dataclass
class InterviewDate:
    """
    Interview date dataclass
    """
    date_id: int
    interview_date: date

    @property
    def date_str(self) -> str:
        """
        Returns the interview date formatted into a string
        :return: Interview date as string
        """
        return self.interview_date.strftime("%b %d, %Y")
