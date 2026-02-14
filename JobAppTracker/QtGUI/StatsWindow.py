from PyQt6.QtWidgets import QWidget

from Data.StatsData import StatsData
from QtGUI.ui.ui_StatsWindow import Ui_StatsWindow

from PyQt6.QtCharts import QPieSeries, QChart, QChartView


class StatsWindow(QWidget):
    """
    Statistics window
    """

    def __init__(self):
        super().__init__()
        self.ui = Ui_StatsWindow()
        self.ui.setupUi(self)

        self.pieSeries = QPieSeries()

        self.chart = QChart()
        self.chart.addSeries(self.pieSeries)
        self.chart.setTitle("Applications Status")
        self.chart.legend().setVisible(False)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self.chartView = QChartView(self.chart)

        self.ui.statsWindowMainLayout.addWidget(self.chartView)

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
        self.ui.cancelledAppsLabel.setText(str(stats_data.cancelled))
        self.ui.declinedAppsLabel.setText(str(stats_data.declined))
        self.ui.jobsInterviewedLabel.setText(str(stats_data.jobs_interviewed))
        self.ui.interviewRateLabel.setText(
            f"{round(stats_data.interview_rate * 100, 2)}%"
        )

        self.chart.removeSeries(self.pieSeries)
        self.pieSeries = QPieSeries()
        self.pieSeries.append("Pending", stats_data.pending)
        self.pieSeries.append("Rejected", stats_data.rejected)
        self.pieSeries.append("Cancelled", stats_data.cancelled)
        self.pieSeries.append("Declined", stats_data.declined)
        self.pieSeries.append("Ghosted", stats_data.ghosted)

        for pieSlice in self.pieSeries.slices():
            pieSlice.setLabelVisible(True)
            pieSlice.setLabel(f"{pieSlice.label()} {round(pieSlice.percentage() * 100, 1)}%")
        self.chart.addSeries(self.pieSeries)

        self.show()
