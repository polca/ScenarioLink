"""
This module contains the models for the tables used in the ScenarioLink plugin.
"""

from urllib.error import HTTPError
import pandas as pd

from activity_browser.ui.tables.models import PandasModel
from ..utils import download_files_from_zenodo
from ..signals import signals


class FoldsModel(PandasModel):
    """
    A model for the Folds table that inherits from PandasModel.

    This model is responsible for fetching and managing the data
    related to different scenarios.
    """

    def __init__(self, parent=None):
        """Initialize the FoldsModel."""
        super().__init__(parent=parent)
        self.selected_record = None

    def sync(self):
        """
        Fetch and synchronize the scenarios list from a remote URL.

        The scenarios list is fetched from a CSV file hosted online.
        The fetched data is then stored in a Pandas DataFrame.
        """
        # URL to fetch scenarios list from
        url = "https://raw.githubusercontent.com/polca/ScenarioLink/main/ab_plugin_scenariolink/scenarios%20list/list.csv"

        try:
            # Prevent fetching a cached file
            # Specify that all columns should be of string type
            dataframe = pd.read_csv(url + "?nocache", header=0, sep=";", dtype=str)

            self._dataframe = dataframe
        except HTTPError as exception:
            print('++Failed to import data:', exception)

        self.updated.emit()

    def get_record(self, idx):
        """Retrieve a record from a selected row in the DataFrame."""
        record = self._dataframe.iat[idx.row(), -1]
        self.selected_record = record
        return record


class DataPackageModel(PandasModel):
    """
    A model for the DataPackage table that inherits from PandasModel.

    This model manages the data related to the datapackages containing
    scenario information.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.data_package = None
        self.include = None

    def sync(self) -> None:
        """
        Synchronize the DataPackage table with the currently loaded data package.

        Reads the descriptor from the data package to build a DataFrame.
        """
        if not self.data_package:
            return

        datapackage = self.data_package
        dataframe = self.build_df_from_descriptor(datapackage.descriptor['scenarios'])
        dataframe = dataframe.reindex(columns=['include', 'name', 'description'])

        self._dataframe = dataframe
        self.updated.emit()

    def build_df_from_descriptor(self, descr: list) -> pd.DataFrame:
        """
        Construct a DataFrame based on the descriptor data.

        Parameters:
            descr (list): A list of dictionaries containing scenario details.

        Returns:
            pd.DataFrame: A DataFrame containing the scenario details.
        """
        if not self.include:
            self.include = [True for _ in descr]
            # if there is only 1 scenario, block SDF enabling
            if len(self.include) <= 1:
                signals.block_sdf.emit(True)

        data = {'include': self.include}

        for dict_ in descr:
            for key, value in dict_.items():
                if data.get(key, False):
                    data[key].append(value)
                else:
                    data[key] = [value]

        self.last_include = self.include
        return pd.DataFrame(data)

    def get_datapackage(self, dp_name: str) -> None:
        """
        Retrieve a datapackage from Zenodo or cache and synchronize the table.

        Parameters:
            dp_name (str): The name of the datapackage to retrieve.
        """
        dp = download_files_from_zenodo(dp_name)
        self.data_package = dp
        self.sync()
