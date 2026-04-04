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
    OFFER = 1
    REJECTED = 2
    DECLINED = 3
    CANCELLED = 4

    # These options are not going to be tied to combobox options, so they
    # have much higher numbers
    INTERVIEW = 63
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
    app_id: int = -1
    company: str = ""
    title: str = ""
    applied_on: date = date.today()
    followed_up: date | None = None
    job_type: JobTypes = JobTypes.IN_PERSON
    location: str = ""
    found_at: str = ""
    website: str = ""
    contact: str = ""
    materials: str = ""
    salary: str = ""
    status: Status = Status.PENDING
    comments: str = ""
    link: str = ""
    description: str = ""
    rej_date: date | None = None
    exp_low: int | None = None
    exp_upp: int | None = None

    @property
    def days_pending(self) -> int:
        """
        Gets the number of days in which the application has been pending
        :return:
        """
        delta = date.today() - self.applied_on
        return delta.days

    @property
    def time_to_rejection(self) -> str:
        if not (self.status == Status.REJECTED or self.status == Status.DECLINED) \
            or self.rej_date is None:
            return ""

        delta = self.rej_date - self.applied_on

        return f"{delta.days}"

    @property
    def experience(self) -> str:
        if self.exp_low is None and self.exp_upp is None:
            return ""

        if self.exp_low is None:
            return f"<{self.exp_upp} YOE"

        if self.exp_upp is None:
            return f"{self.exp_low}+ YOE"

        return f"{self.exp_low}-{self.exp_upp} YOE"
