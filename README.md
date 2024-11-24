# Strava File Uploader

Supports uploading TCX and FIT file formats to Strava

## Usage

Given a directory of TCX and/or FIT files, run the following:

1. `file_builder.py`: Generates a CSV file containing metadata of the files to upload to Strava. Run this first.
2. `strava_upload.py`: Get an access token (numerous ways but you can see it in your API keys on the website). Run the command with the csv file you wish to upload (one each is generated for TCX and FIT), and the access token as parameters

If you want to inspect the contents of a FIT file, you can use `fitviewer.py`. Pass the filename as an argument.

The project has a couple of dependencies in `pyproject.toml`. You can run the scripts via `poetry`, e.g. `poetry run python ./file_builder.py ...` etc.

## Usage notes

At the time of writing, Strava imposes a limit of 250 uploads via the API per 15 mins and 2000 API calls overall, per day. The script will detect when the upload limit has been reached, and then try again 15 minutes later. If the 2000 limit is reached then you have to wait 24 hours...

If an upload fails and you want to start again, then inspect the log file for the last successfully loaded filename. You can then edit the CSV file to remove all the files prior to, and including that file, and start the upload script again.
