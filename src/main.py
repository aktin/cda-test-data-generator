import os
import toml
import argparse

from generate_csv import generate_csv
from csv_to_cda import csv_to_cda
from calculate_dependencies import calculate_dependencies
from src.sent_to_server_and_print_error import send_xml_file

if __name__ == '__main__':
    # Load configuration from config.toml
    config = toml.load('../config.toml')

    # Set environment variables
    os.environ['CSV_PATH'] = config['cda_paths']['csv_path']
    os.environ['EXCEL_PATH'] = config['cda_paths']['excel_path']
    os.environ['XSLT_FILE'] = config['cda_paths']['xslt_file']

    # Get environment variables
    csv_path = os.environ['CSV_PATH']
    excel_path = os.environ['EXCEL_PATH']
    xslt_file = os.environ['XSLT_FILE']

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process CSV to CDA.')
    parser.add_argument('--rows', type=int, required=True, help='Number of rows to generate in the CSV file')
    args = parser.parse_args()

    # First step: Generate csv with rows as patients
    generate_csv(excel_path, csv_path, 10)
    # Second step: Set dependable variables
    calculate_dependencies(csv_path)
    # Third step: Transform to CDA
    csv_to_cda(csv_path, xslt_file)

    # for i in range(1, 11):
    #     send_xml_file("http://localhost:5080/aktin/cda/fhir/Binary/$validate", f"../output/cda/cda_{i}.xml",
    #                   f"../output/fehlercodes/response{i}.xml")

    # Remove data.csv
    os.remove(csv_path)

