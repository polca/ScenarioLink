import pandas as pd
from urllib.error import HTTPError
from activity_browser.ui.tables.models import PandasModel
from ..utils import download_files_from_zenodo

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


class DataPackageModel(PandasModel):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.data_package = None

    def sync(self):
        if not self.data_package:
            return

        dp = self.data_package
        self._dataframe = self.build_df_from_descriptor(dp.descriptor['scenarios'])
        self.updated.emit()

    def build_df_from_descriptor(self, descr):
        data = {}
        for dict_ in descr:
            for key, value in dict_.items():
                if data.get(key, False):
                    data[key].append(value)
                else:
                    data[key] = [value]
        return pd.DataFrame(data)

    def get_datapackage(self, dp_name: str):
        dp = download_files_from_zenodo(dp_name)
        self.data_package = dp
        self.sync()
