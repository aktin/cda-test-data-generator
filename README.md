# CDA Processing and Validation

This project processes CSV files into CDA (Clinical Document Architecture) XML files, transforms them using XSLT, and validates the resulting XML files by sending them to a server.

## Project Structure

- `src/`
  - `main.py`: Main script to run the entire process.
  - `generate_csv.py`: Generates CSV files from an Excel file.
  - `csv_to_cda.py`: Converts CSV files to CDA XML files using XSLT.
  - `calculate_dependencies.py`: Calculates dependencies for the CSV data.
  - `sent_to_server_and_print_error.py`: Sends XML files to a server for validation and prints any errors.
- `res/`
  - `CDAVariables.xlsx`: Source Excel file for generating CSV.
  - `EmergencyNote.xslt`: XSLT file for transforming CSV data to CDA XML.
  - `stylesheets/`: Directory containing XSL stylesheets.
  - `schematron-basis/`: Directory containing Schematron files.
- `output/`
  - `raw/`: Directory for storing raw XML files.
  - `cda/`: Directory for storing CDA XML files.
  - `fehlercodes/`: Directory for storing server response files.

## Requirements

- Python 3.x
- `requests` library
- `lxml` library

Install the required libraries using:
```sh
pip install requests lxml