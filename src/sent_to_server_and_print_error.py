import requests




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


if __name__ == '__main__':

    send_xml_file("http://localhost:5080/aktin/cda/fhir/Binary/$validate", "../output/cda/cda_7.xml",
                  "../output/fehlercodes/response.xml")
