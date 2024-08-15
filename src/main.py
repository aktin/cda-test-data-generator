import os
import toml
import argparse

from generate_csv import generate_csv
from csv_to_cda import csv_to_cda
from calculate_dependencies import calculate_dependencies
from src.sent_to_server_and_print_error import send_xml_file


def main():
    global config, parser, args, rows
    # Load configuration from config.toml
    config = toml.load('../config.toml')
    # Set environment variables TODO
    os.environ['CSV_PATH'] = config['cda_paths']['csv_path']
    os.environ['EXCEL_PATH'] = config['cda_paths']['excel_path']
    os.environ['XSLT_FILE'] = config['cda_paths']['xslt_file']
    os.environ['OUTPUT_DIR'] = config['cda_paths']['output_dir']
    os.environ['CITIES_CSV'] = config['csv_paths']['cities_csv']
    # Get environment variables
    csv_path = os.environ['CSV_PATH']
    excel_path = os.environ['EXCEL_PATH']
    xslt_file = os.environ['XSLT_FILE']
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process Excel to CDA.')
    parser.add_argument('--rows', type=int, required=True, help='Number of rows to generate in the CSV file')
    args = parser.parse_args()
    rows = args.rows
    # First step: Generate csv with rows as patients
    generate_csv(excel_path, csv_path, rows)
    # Second step: Set dependable variables
    calculate_dependencies(csv_path)
    # Third step: Transform to CDA
    csv_to_cda(csv_path, xslt_file)
    # Remove data.csv
    # os.remove(csv_path)


if __name__ == '__main__':
    main()
