import pandas as pd
from activity_browser.ui.tables.models import PandasModel

class FoldsModel(PandasModel):
    HEADERS = [""]

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def sync(self):

        # url to fetch scenarios list form
        url = "https://raw.githubusercontent.com/polca/ScenarioLink/main/ab_plugin_scenarioLink/scenarios%20list/list.csv"
        # load pandas dataframe from url
        # and specificy that the first row has headers
        self._dataframe = pd.read_csv(url, header=0)
        self.updated.emit()