import requests
import zipfile
import os
from datapackage import Package
import appdirs


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
    folder_name = appdirs.user_cache_dir('activity-browser', 'polca')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Create a ZIP file to store the downloaded files
    zip_filename = f"{record_id}.zip"

    # check first if file exists, otherwise download it
    if os.path.exists(f"{folder_name}/{zip_filename}"):
        return Package(f"{folder_name}/{zip_filename}")

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for idx, file_info in enumerate(json_data['files']):
            print(f"Downloading file {idx + 1}/{len(json_data['files'])}")

            file_url = file_info['links']['self']
            r = requests.get(file_url)

            # Save the file to the folder
            local_filename = os.path.join(folder_name, zip_filename)

            with open(local_filename, 'wb') as f:
                f.write(r.content)

            # Add the files to the ZIP archive
            zipf.write(local_filename, os.path.basename(local_filename))

    return Package(f"{folder_name}/{zip_filename}")



