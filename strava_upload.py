import csv
import time
import logging
import requests
import argparse  # Add argparse import

# Configure logging
logging.basicConfig(
    filename='upload_errors.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger().addHandler(logging.StreamHandler())  # Also log to console

# Strava API endpoint and access token
STRAVA_UPLOAD_URL = 'https://www.strava.com/api/v3/uploads'

def upload_activity(file_path, activity_type, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    files = {
        'file': open(file_path, 'rb'),
        'data_type': (None, 'fit' if file_path.endswith('.fit') else 'tcx'),
        'activity_type': (None, activity_type)
    }
    response = requests.post(STRAVA_UPLOAD_URL, headers=headers, files=files)
    return response

def main(csv_file, access_token):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        call_count = 0
        start_time = time.time()

        for row in reader:            
            file_path = row['Filename']
            activity_type = row['Activity Type']
            
            try:
                response = upload_activity(file_path, activity_type, access_token)
                if response.status_code == 429:  # Rate limit exceeded
                    logging.error("Rate limit exceeded. Waiting for reset.")
                    time.sleep(900)  # Wait for 15 minutes
                    start_time = time.time()
                    call_count = 0
                    response = upload_activity(file_path, activity_type, access_token)
                
                if response.status_code == 201:
                    logging.info(f"Successfully uploaded {file_path}")
                else:
                    logging.error(f"Failed to upload {file_path}: {response.text}")
                
                call_count += 1
                if call_count >= 250:
                    elapsed_time = time.time() - start_time
                    if elapsed_time < 900:
                        time.sleep(900 - elapsed_time)
                    start_time = time.time()
                    call_count = 0

            except Exception as e:
                logging.error(f"Error uploading {file_path}: {str(e)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload activities to Strava.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file containing activity data')
    parser.add_argument('access_token', type=str, help='Strava API access token')
    args = parser.parse_args()
    
    main(args.csv_file, args.access_token)