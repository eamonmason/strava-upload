import argparse  # Add argparse import
import csv
import logging
import os
import time
from datetime import datetime

import requests


def setup_logging(
    log_level: int = logging.INFO, logger_name: str = __name__
) -> logging.Logger:
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create logs subfolder if it doesn't exist
    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    formatter = logging.Formatter(log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(os.path.join(log_folder, f"{timestamp}.log"))
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


def configure_logging(func):
    def wrapper(*args, **kwargs):
        logger = setup_logging()
        kwargs["logger"] = logger
        return func(*args, **kwargs)

    return wrapper


# Strava API endpoint and access token
STRAVA_UPLOAD_URL = "https://www.strava.com/api/v3/uploads"


def upload_activity(
    file_path: str, activity_type: str, access_token: str
) -> requests.Response:
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {
        "file": open(file_path, "rb"),
        "data_type": (None, "fit" if file_path.endswith(".fit") else "tcx"),
        "activity_type": (None, activity_type),
    }
    response = requests.post(STRAVA_UPLOAD_URL, headers=headers, files=files)
    return response


@configure_logging
def main(csv_file: str, access_token: str, logger=None):
    logger = kwargs["logger"]
    try:
        with open(csv_file, "r") as file:
            reader = csv.DictReader(file)
            call_count = 0
            start_time = time.time()

            for row in reader:
                file_path = row["Filename"]
                activity_type = row["Activity Type"]

                try:
                    response = upload_activity(file_path, activity_type, access_token)
                    if response.status_code == 429:  # Rate limit exceeded
                        logger.error("Rate limit exceeded. Waiting for reset.")
                        time.sleep(900)  # Wait for 15 minutes
                        start_time = time.time()
                        call_count = 0
                        response = upload_activity(
                            file_path, activity_type, access_token
                        )

                    if response.status_code == 201:
                        logger.info(f"Successfully uploaded {file_path}")
                    elif response.status_code == 401:
                        logger.error(
                            "Invalid access token. Please check your access token."
                        )
                        break
                    else:
                        logger.error(
                            f"Failed to upload {file_path}: {response.status_code} - {response.text}"
                        )

                    call_count += 1
                    if call_count >= 250:
                        elapsed_time = time.time() - start_time
                        if elapsed_time < 900:
                            time.sleep(900 - elapsed_time)
                        start_time = time.time()
                        call_count = 0

                except Exception as e:
                    logger.error(f"Error uploading {file_path}: {str(e)}")
                    raise e

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload activities to Strava.")
    parser.add_argument(
        "csv_file", type=str, help="Path to the CSV file containing activity data"
    )
    parser.add_argument("access_token", type=str, help="Strava API access token")
    args = parser.parse_args()

    main(args.csv_file, args.access_token)
