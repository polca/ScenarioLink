import requests
import zipfile
import os
import tempfile
from datapackage import Package
import appdirs
from ...signals import signals
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt


def download_files_from_zenodo(record_id):
    # Define the API endpoint
    url = f"https://zenodo.org/api/records/{record_id}"
    print(url)

    # Send a GET request to fetch the raw JSON content
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to get data from Zenodo. Status code: {response.status_code}")
        return

    json_data = response.json()

    # Create a folder to save the files
    folder_name = appdirs.user_cache_dir('ActivityBrowser', 'ActivityBrowser')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Create a ZIP file to store the downloaded files
    zip_filename = f"{record_id}.zip"

    # check first if file exists, otherwise download it
    if os.path.exists(os.path.join(folder_name, zip_filename)):
        return Package(os.path.join(folder_name, zip_filename))

    signals.downloading_label.emit()

    QApplication.setOverrideCursor(Qt.WaitCursor)
    with zipfile.ZipFile(os.path.join(folder_name, zip_filename), 'w') as final_zip:
        for idx, file_info in enumerate(json_data['files']):
            print(f"Downloading file {idx + 1}/{len(json_data['files'])}")

            file_url = file_info['links']['self']
            r = requests.get(file_url)

            # Create a temporary directory to hold the downloaded ZIP files and their extracted contents
            with tempfile.TemporaryDirectory() as tmpdirname:
                downloaded_zip_path = os.path.join(tmpdirname, "downloaded.zip")

                # Save the downloaded ZIP file
                with open(downloaded_zip_path, 'wb') as f:
                    f.write(r.content)

                # Extract the downloaded ZIP file
                with zipfile.ZipFile(downloaded_zip_path, 'r') as downloaded_zip:
                    downloaded_zip.extractall(tmpdirname)

                # Walk through the extracted files and add them to the final ZIP file
                for root, _, files in os.walk(tmpdirname):
                    for file in files:
                        final_zip.write(os.path.join(root, file), file)




    QApplication.restoreOverrideCursor()
    return Package(os.path.join(folder_name, zip_filename))



