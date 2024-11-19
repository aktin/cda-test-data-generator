# CSV to CDA Processor ![Python 3.12](https://img.shields.io/badge/python-3.12-blue)

A Python-based tool for generating test Clinical Document Architecture (CDA) files from Excel templates. This project helps healthcare IT professionals create sample AKTIN CDA documents for testing and development purposes of the AKTIN DWH.

## Prerequisites

- Python 3.12
- `pip` (Python package installer)

## Installation

1. Clone the repository:
```sh
git clone https://github.com/aktin/cda-test-data-generator
cd https://github.com/aktin/cda-test-data-generator
```
2. Install the required Python packages:
```sh
pip install -r requirements.txt
```

## Configuration
The tool requires two main configuration files:

1. Excel Template (`*.xlsx`):
    * Defines the structure and constraints for CSV generation
    * Located in the `resources` directory by default 
    * Must follow the specified template format (see Documentation)


2. XSLT Template (`*.xslt`):
    * Defines the transformation from CSV to CDA 
    * Located in the `resources` directory by default 
    * Must be valid XSLT 1.0 or 2.0

## Usage

Navigate to the `src` directory and run:
```sh
python main.py --n <number_of_CDAs> --xslt <xslt_file> --xlsx <excel_file> [--o <output_dir>][--cleanup]
```

### Parameters

| Parameter | Required | Description                         | Default |
|-----------|----------|-------------------------------------|---------|
| `--n` | Yes | Number of CDA documents to generate | None |
| `--xslt` | Yes | Relative path to XSLT template file | None |
| `--xlsx` | Yes | Relative path to Excel template file         | None |
| `--o` | No | Output directory for CDA files      | `<repository-directory>/output` |
| `--cleanup` | No | Remove intermediate CSV files       | `False` |

### Example

To generate a CSV file with 10 rows (and 10 test CDAs respectively), run:
```sh
python main.py --n 10 --xlsx ../resources/CDAVariables_short.xlsx --xslt ../resources/EmergencyNote.xslt --o ../output
```

## License

This project is licensed under the AGPL-3.0 license.
