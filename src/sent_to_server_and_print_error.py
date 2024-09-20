import argparse

import requests
from lxml import etree

from src import main

def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Process CDA files and analyze responses.")
    parser.add_argument('--n', type=int, default=None,
                        help="Number of rows to process. If not provided, will process all files in the CDA directory.")
    parser.add_argument('--config', type=str, required=True, help='Filepath for configuration TOML file.')
    parser.add_argument('--cleanup', action='store_true', help='Remove intermediate CSV file after processing.')

    return parser.parse_args()


def send_xml_file(url: str, xml_file_path: str, response_file_path: str) -> None:
    try:
        # Read the XML file
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_data = file.read()

        # Set the headers
        headers = {'Content-Type': 'application/xml'}

        # Send the POST request with the XML data
        response = requests.post(url, data=xml_data, headers=headers)
        print(response.status_code)
        # Write the response to a file
        with open(response_file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)

        print(f'Response written to {response_file_path}')
        print(response.text)

    except Exception as e:
        print(f'An error occurred: {e}')


def main_and_sent_test():
    args = parse_arguments()
    main.main()
    rows = args.n
    for i in range(rows):
        send_xml_file("http://localhost:9090/aktin/cda/fhir/Binary/$validate", f"C:\\Users\\alexa\PycharmProjects\cda-test-data-generator\output\cda\cda_{i+1}.cda",
                      f"../output/fehlercodes/response_{i+1}.xml")



if __name__ == '__main__':
    main_and_sent_test()

