# CSV to CDA Processor

This project processes CSV files to generate CDA (Clinical Document Architecture) files. It reads configuration from a `config.toml` file, sets environment variables, and processes the data through several steps.

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

3. Ensure you have the following structure in your `config.toml` file:
    ```toml
    [cda_paths]
    csv_path = "../resources/data.csv"
    excel_path = "../resources/CDAVariables.xlsx"
    xslt_file = "../resources/EmergencyNote.xslt"
    ```

## Usage

1. Navigate to the `src` directory:
    ```sh
    cd src
    ```

2. Run the main script with the required command line argument for the number of rows:
    ```sh
    python main.py --rows <number_of_rows>
    ```

    Replace `<number_of_rows>` with the number of rows you want to generate in the CSV file.

## Configuration

The `config.toml` file should be located in the root directory of the project. It contains paths to the necessary files:
- `csv_path`: Path to the CSV file.
- `excel_path`: Path to the Excel file.
- `xslt_file`: Path to the XSLT file.

Example `config.toml`:
```toml
[cda_paths]
csv_path = "../resources/data.csv"
excel_path = "../resources/CDAVariables.xlsx"
xslt_file = "../resources/EmergencyNote.xslt"
```

## Main Script

The main script (`main.py`) performs the following steps:

1. Loads configuration from `config.toml`.
2. Sets environment variables based on the configuration.
3. Parses command line arguments to get the number of rows.
4. Generates a CSV file with the specified number of rows.
5. Calculates dependencies and updates the CSV file.
6. Transforms the CSV file to CDA format.
7. Optionally sends the generated CDA files to a server for validation (commented out by default).
8. Removes the generated CSV file.

## Example

To generate a CSV file with 10 rows and process it, run:
```sh
python main.py --rows 10
```

## License

This project is licensed under the AGPL-3.0 license.
