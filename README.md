# CDA Test Data Generator

This project generates synthetic CDA (Clinical Document Architecture) files. 
It reads an Excel file with the required variables and generates a CSV file with the specified number of rows. The CSV file is then transformed into CDA format using an XSLT file.

## Prerequisites

- Python 3.12
- `pip` (Python package installer)

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Navigate to the `src` directory:
    ```sh
    cd src
    ```

2. Run the main script with the required command line argument for the number of rows:
    ```sh
    python main.py --n <number_of_CDAs> --xslt <xslt_file> --xlsx <excel_file> [--o <output_dir>][--cleanup]
    ```

    - `--n <number_of_CDAs>`: Number of CDAs to generate.
    - `--xslt <xslt_file>`: relative Path to the XSLT file.
    - `--xlsx <excel_file>`: relative Path to the Excel file.
    - `--o <output_dir>`: [optional] Output directory for the generated CDAs (default: <repository-directory>/output).
    - `--cleanup`: [optional] Remove the generated CSV file.
    


## Main Script

The main script (`main.py`) performs the following steps:


1. Sets environment variables based on input arguments.
2. Reads the Excel file with the required variables.
3. Generates a CSV file with the specified number of rows.
4. Calculates dependencies and updates the CSV file.
5. Transforms the CSV file to CDA format.
6. Saves the generated CDAs to the output directory.

## Example

To generate a CSV file with 10 rows and process it, run:
   ```sh
   python main.py --n 10 --xlsx ../resources/CDAVariables_short.xlsx --xslt ../resources/EmergencyNote.xslt --o ../output
   ```

## License

This project is licensed under the AGPL-3.0 license.
