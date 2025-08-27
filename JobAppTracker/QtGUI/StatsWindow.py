from PyQt6.QtWidgets import QWidget

from Data.StatsData import StatsData
from QtGUI.ui.ui_StatsWindow import Ui_StatsWindow


class StatsWindow(QWidget):
    """
    Statistics window
    """

    def __init__(self):
        super().__init__()
        self.ui = Ui_StatsWindow()
        self.ui.setupUi(self)

    def load_stats_and_show(self, stats_data: StatsData) -> None:
        """
        Loads statistics into the window before showing it
        :param stats_data: Statistics data
        :return: 
        """
        if self.isVisible():
            return

        self.ui.totalAppsLabel.setText(str(stats_data.total_apps))
        self.ui.numInterviewsLabel.setText(str(stats_data.total_num_interviews))
        self.ui.avgIntsPerJobLabel.setText(str(
            round(stats_data.avg_ints_per_job, 2)
        ))
        self.ui.avgAppsPerMonthLabel.setText(str(
            round(stats_data.avg_apps_per_month, 2)
        ))
        self.ui.pendingAppsLabel.setText(str(stats_data.pending))
        self.ui.rejectedAppsLabel.setText(str(stats_data.rejected))
        self.ui.ghostedAppsLabel.setText(str(stats_data.ghosted))
        self.ui.jobsInterviewedLabel.setText(str(stats_data.jobs_interviewed))
        self.ui.interviewRateLabel.setText(
            f"{round(stats_data.interview_rate * 100, 2)}%"
        )

        self.show()
