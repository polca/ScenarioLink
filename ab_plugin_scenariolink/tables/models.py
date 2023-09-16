import pandas as pd
from urllib.error import HTTPError
from activity_browser.ui.tables.models import PandasModel

class FoldsModel(PandasModel):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def sync(self):
        # url to fetch scenarios list form
        url = "https://raw.githubusercontent.com/polca/ScenarioLink/main/ab_plugin_scenariolink/scenarios%20list/list.csv"
        # load pandas dataframe from url
        # and specify that the first row has headers
        try:
            # prevent fetching cached file
            # and specific that all columns should be of string type
            df = pd.read_csv(url + "?nocache", header=0, sep=";", dtype=str)

            self._dataframe = df
        except HTTPError as e:
            print('++failed to import data', e)

        self.updated.emit()

    def get_record(self, idx):
        return self._dataframe.iat[idx.row(), -1]

