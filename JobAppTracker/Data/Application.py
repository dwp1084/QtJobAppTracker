from dataclasses import dataclass
from datetime import date

JOB_TYPES = ["In Person", "Hybrid", "Remote"]
STATUS = ["Pending", "Interview", "Offer", "Rejected"]


@dataclass
class Application:
    app_id: int
    company: str
    title: str
    applied_on: date
    followed_up: date
    job_type: int
    location: str
    website: str
    contact: str
    materials: str
    salary: str
    status: int
    comments: str

    def get_job_type_name(self):
        return JOB_TYPES[self.job_type]

    def get_status_name(self):
        return STATUS[self.status]

    @property
    def days_pending(self):
        delta = date.today() - self.applied_on
        return delta.days
