from generate_csv import generate_csv
from csv_to_cda import csv_to_cda
from calculate_dependencies import calculate_dependencies
from src.sent_to_server_and_print_error import send_xml_file

if __name__ == '__main__':
    csv_path = '../resources/data.csv'
    excel_path = '../resources/CDAVariables.xlsx'
    xslt_file = '../resources/EmergencyNote.xslt'

    # First step: Generate
    generate_csv(excel_path, csv_path, 10)
    # Second step: Set dependable variables
    calculate_dependencies(csv_path)
    # Third step: Transform to CDA
    csv_to_cda(csv_path, xslt_file)

    for i in range(1,11):
        send_xml_file("http://localhost:5080/aktin/cda/fhir/Binary/$validate", f"../output/cda/cda_{i}.xml",
                  f"../output/fehlercodes/response{i}.xml")