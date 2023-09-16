import pandas as pd
from activity_browser.ui.tables.models import PandasModel

class FoldsModel(PandasModel):
    HEADERS = [""]

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def sync(self):

        self._dataframe = pd.read_csv("https://github.com/polca/ScenarioLink/blob/main/ab_plugin_scenarioLink/scenarios%20list/list.csv")
        self.updated.emit()