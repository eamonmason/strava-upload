from fitparse import FitFile
import argparse

def show_fit_contents(file_path):
    fitfile = FitFile(file_path)
    
    for record in fitfile.get_messages():
        print(f"Record: {record.name}")
        for data in record:
            print(f"  {data.name}: {data.value}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='View contents of a FIT file.')
    parser.add_argument('file_path', type=str, help='Path to the FIT file')
    args = parser.parse_args()
    
    show_fit_contents(args.file_path)