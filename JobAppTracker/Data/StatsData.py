from dataclasses import dataclass


@dataclass
class StatsData:
    """
    Dataclass for the statistics that can be gathered from app table data and
    then passed to statistics window
    """
    total_apps: int
    total_num_interviews: int
    avg_ints_per_job: float
    avg_apps_per_month: float
    jobs_interviewed: int
    leaderboard: list[tuple[str, int]]
    pending: int = 0
    rejected: int = 0
    ghosted: int = 0
    declined: int = 0
    cancelled: int = 0

    @property
    def interview_rate(self) -> float:
        """
        Number of jobs interviewed over the total number of applications sent
        :return:
        """
        return self.jobs_interviewed / self.total_apps
