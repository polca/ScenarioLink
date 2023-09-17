"""
Models for the tables in the plugin.
"""

from urllib.error import HTTPError
import pandas as pd

from activity_browser.ui.tables.models import PandasModel

from ..utils import download_files_from_zenodo

class FoldsModel(PandasModel):
    """
    Model for the Folds table.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def sync(self):
        # url to fetch scenarios list from
        url = "https://raw.githubusercontent.com/polca/ScenarioLink/main/ab_plugin_scenariolink/scenarios%20list/list.csv"
        # load pandas dataframe from url
        # and specify that the first row has headers
        try:
            # prevent fetching cached file
            # and specific that all columns should be of string type
            dataframe = pd.read_csv(url + "?nocache", header=0, sep=";", dtype=str)

            self._dataframe = dataframe
        except HTTPError as exception:
            print('++failed to import data', exception)

        self.updated.emit()

    def get_record(self, idx):
        """Get record from selected row."""
        return self._dataframe.iat[idx.row(), -1]


class DataPackageModel(PandasModel):
    """
    Model for the DataPackage table.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.data_package = None
        self.include = []

    def sync(self) -> None:
        if not self.data_package:
            return
        datapackage = self.data_package
        dataframe = self.build_df_from_descriptor(datapackage.descriptor['scenarios'])
        dataframe = dataframe.reindex(columns=['include', 'name', 'description'])
        self._dataframe = dataframe
        self.updated.emit()

    def build_df_from_descriptor(self, descr: list) -> pd.DataFrame:
        """Build dataframe from descriptor data."""
        if not self.include:
            self.include = [True for _ in descr]
        data = {'include': self.include}
        for dict_ in descr:
            for key, value in dict_.items():
                if data.get(key, False):
                    data[key].append(value)
                else:
                    data[key] = [value]
        return pd.DataFrame(data)

    def get_datapackage(self, dp_name: str) -> None:
        """Retrieve datapackage (from zenodo or cache) and sync table."""
        dp = download_files_from_zenodo(dp_name)
        self.data_package = dp
        self.sync()
