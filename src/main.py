from generate_csv import generate_csv
from csv_to_cda import csv_to_cda
from calculate_dependencies import calculate_dependencies
from src.sent_to_server_and_print_error import send_xml_file

if __name__ == '__main__':
    
    data_csv = generate_csv('../resources/CDAVariables.xlsx', 10)

    print()
    calculate_dependencies(data_csv)

    xslt_file = '../resources/EmergencyNote.xslt'
    csv_to_cda(data_csv, xslt_file)
    for i in range(1,11):
        send_xml_file("http://localhost:5080/aktin/cda/fhir/Binary/$validate", f"../output/cda/cda_{i}.xml",
                  f"../output/fehlercodes/response{i}.xml")