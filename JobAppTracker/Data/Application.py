from dataclasses import dataclass
from datetime import date
from enum import Enum


class JobTypes(Enum):
    """
    Job type enumeration
    """
    IN_PERSON = 0
    HYBRID = 1
    REMOTE = 2

    def __str__(self):
        return self.name.capitalize().replace("_", " ")

    def __int__(self):
        return self.value


class Status(Enum):
    """
    Application status enumeration
    """
    PENDING = 0
    INTERVIEW = 1
    OFFER = 2
    REJECTED = 3

    # This one is different as it's not meant to be stored in db
    LIKELY_GHOSTED = 64

    def __str__(self):
        return self.name.capitalize().replace("_", " ")

    def __int__(self):
        return self.value


@dataclass
class Application:
    """
    Application dataclass
    """
    app_id: int
    company: str
    title: str
    applied_on: date
    followed_up: date
    job_type: JobTypes
    location: str
    website: str
    contact: str
    materials: str
    salary: str
    status: Status
    comments: str

    @property
    def days_pending(self) -> int:
        """
        Gets the number of days in which the application has been pending
        :return:
        """
        delta = date.today() - self.applied_on
        return delta.days
