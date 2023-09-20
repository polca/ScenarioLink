"""
Utility functions for the ScenarioLink plugin.
This module contains various utility functions that are used throughout the plugin.
"""

import zipfile
import os
import tempfile
import requests
from unfold import Unfold
from datapackage import Package
import appdirs
import pandas as pd
import io
from importlib.metadata import version, PackageNotFoundError
from typing import Tuple

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt


def unfold_databases(
        filename: str,
        scenarios: list,
        dependencies: dict,
        superstructure: bool,
        superstructure_db_name: str) -> None:
    """
    Unfold databases based on a given filepath and scenarios list.

    Parameters:
        filename (str): The path to the database file.
        scenarios (list): The list of scenarios to unfold.
        dependencies (dict): A dictionary containing dependencies.
        superstructure (bool): Flag to indicate if a superstructure should be unfolded.
        superstructure_db_name

    Returns:
        None: This function performs the unfolding operation but does not return anything.
    """

    cache_folder = appdirs.user_cache_dir('ActivityBrowser', 'ActivityBrowser')
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    filename = f"{filename}.zip"
    filepath = os.path.join(cache_folder, os.path.basename(filename))

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist.")

    try:
        Unfold(filepath).unfold(
            dependencies=dependencies,
            scenarios=scenarios,
            superstructure=superstructure,
            name=superstructure_db_name
        )
    except Exception as e:
        print(f"Failed to unfold database: {e}")
        return


def download_files_from_zenodo(record_id: str) -> [Package, None]:
    """
    Download datapackages from Zenodo based on a given record ID.

    Parameters:
        record_id (str): The Zenodo record ID.

    Returns:
        Package: A datapackage object containing the downloaded files.
        None: Returns None if the download fails.
    """

    # Zenodo API endpoint to fetch datapackages
    url = f"https://zenodo.org/api/records/{record_id}"

    # Create a folder to save the downloaded files
    folder_name = appdirs.user_cache_dir('ActivityBrowser', 'ActivityBrowser')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print("Cache folder: ", folder_name)

    # Define the ZIP filename based on the Zenodo record ID
    zip_filename = f"{record_id}.zip"

    # Check if the file already exists; if so, return the Package
    if record_cached(record_id):
        print(f"File {zip_filename} already exists in cache.")
        return Package(os.path.join(folder_name, zip_filename))

    print(f"Fetching data from Zenodo: {url}")

    # Perform GET request to fetch the raw JSON content
    response = requests.get(url, timeout=10)

    # Handle unsuccessful requests
    if response.status_code != 200:
        print(f"Failed to get data from Zenodo. Status code: {response.status_code}")
        return None

    json_data = response.json()

    # Change cursor to indicate ongoing process
    QApplication.setOverrideCursor(Qt.WaitCursor)

    # Create a final ZIP file to store the downloaded files
    with zipfile.ZipFile(os.path.join(folder_name, zip_filename), 'w') as final_zip:
        for idx, file_info in enumerate(json_data['files']):
            print(f"Downloading file {idx + 1}/{len(json_data['files'])}")

            file_url = file_info['links']['self']
            response = requests.get(file_url, timeout=10)

            # Create a separate temporary directory to store the downloaded ZIP files
            with tempfile.TemporaryDirectory() as download_tmpdirname:
                downloaded_zip_path = os.path.join(download_tmpdirname, "downloaded.zip")

                # Save the downloaded ZIP file locally
                with open(downloaded_zip_path, 'wb') as file:
                    file.write(response.content)

                # Create another temporary directory for the extracted files
                with tempfile.TemporaryDirectory() as extract_tmpdirname:
                    # Extract the ZIP file's contents
                    with zipfile.ZipFile(downloaded_zip_path, 'r') as downloaded_zip:
                        downloaded_zip.extractall(extract_tmpdirname)

                    # Add the extracted files to the final ZIP file
                    for root, _, files in os.walk(extract_tmpdirname):
                        for file in files:
                            # Calculate the relative path
                            relative_path = os.path.relpath(os.path.join(root, file), extract_tmpdirname)
                            # Add the file to the ZIP archive with its relative path
                            final_zip.write(os.path.join(root, file), relative_path)
        print("Done.")
    # Restore the original cursor
    QApplication.restoreOverrideCursor()

    return Package(os.path.join(folder_name, zip_filename))

def package_from_path(path: str) -> [Package, None]:
    """Create a package from the selected zip file"""
    if not path.endswith('.zip'):
        print("Error, file selected is not a .zip file.")
        return
    return Package(path)

def record_cached(record: str) -> bool:
    """Return if record is cached."""
    folder_name = appdirs.user_cache_dir('ActivityBrowser', 'ActivityBrowser')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    zip_filename = record + '.zip'
    return os.path.exists(os.path.join(folder_name, zip_filename))

class UpdateManager():

    @classmethod
    def get_versions(cls) -> Tuple[str, str, bool]:
        """Get the version of this plugin and the most recent version.

        Return (current, latest, newer)
        newer is a bool which is true if there is a newer version
        """
        current = cls._current_version(cls)
        latest = cls._fetch_latest(cls)

        for c, l in zip(current.split('.'), latest.split('.')):
            if int(l) > int(c):
                return (True, current, latest)
        return (False, current, latest)

    def _fetch_latest(self) -> str:
        """Fetch the latest version number from conda channel."""
        try:
            package_url = 'https://anaconda.org/romainsacchi/ab-plugin-scenariolink/labels'
            page = requests.get(package_url)  # retrieve the page from the URL
            df = pd.read_html(io.StringIO(page.text))[0]  # read the version table from the HTML
            latest = df.iloc[0, 1]
        except:  # TODO log error properly and handle it properly
            latest = '0.0.0'
        return latest

    def _current_version(self) -> str:
        """Version of ScenarioLink running now."""
        try:
            version_ = version(__package__)
        except PackageNotFoundError:
            version_ = "0.0.0"
        return version_
