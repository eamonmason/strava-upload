import os
import csv
import xml.etree.ElementTree as ET
from fitparse import FitFile

def parse_tcx_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    
    activity = root.find('.//ns:Activity', namespace)
    activity_type = activity.get('Sport') if activity is not None else 'Unknown'
    if activity_type == 'Running':
        activity_type = 'Run'
    elif activity_type == 'Biking' or activity_type == 'Cycling':
        activity_type = 'Ride'

    return {
        'External ID': os.path.basename(file_path),
        'Activity Type': activity_type,
        'Name': activity_type,
        'Description': '',
        'Commute?': 'false',
        'Trainer?': 'false',
        'File Type': 'tcx',
        'Filename': os.path.basename(file_path)
    }

def parse_fit_file(file_path):
    fitfile = FitFile(file_path)
    activity_type = 'Unknown'
    
    for record in fitfile.get_messages('sport'):
        for data in record:
            if data.name == 'sport':
                activity_type = data.value
                break
    
    if activity_type == 'running':
        activity_type = 'Run'
    elif activity_type == 'cycling':
        activity_type = 'Ride'

    return {
        'External ID': os.path.basename(file_path),
        'Activity Type': activity_type,
        'Name': activity_type,
        'Description': '',
        'Commute?': 'false',
        'Trainer?': 'false',
        'File Type': 'fit',
        'Filename': os.path.basename(file_path)
    }

def generate_csv_from_tcx(directory, output_csv):
    fieldnames = ['External ID', 'Activity Type', 'Name', 'Description', 'Commute?', 'Trainer?', 'File Type', 'Filename']
    rows = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.tcx'):
            file_path = os.path.join(directory, filename)
            row = parse_tcx_file(file_path)
            rows.append(row)
    
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def generate_csv_from_fit(directory, output_csv):
    fieldnames = ['External ID', 'Activity Type', 'Name', 'Description', 'Commute?', 'Trainer?', 'File Type', 'Filename']
    rows = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.fit'):
            file_path = os.path.join(directory, filename)
            row = parse_fit_file(file_path)
            rows.append(row)
    
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# Example usage
directory = '.'
output_csv = 'output_tcx.csv'
generate_csv_from_tcx(directory, output_csv)

output_csv = 'output_fit.csv'
generate_csv_from_fit(directory, output_csv)
