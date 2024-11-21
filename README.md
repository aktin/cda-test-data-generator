# CSV to CDA Processor ![Python 3.12](https://img.shields.io/badge/python-3.12-blue)

A Python-based tool for generating test Clinical Document Architecture (CDA) files from Excel templates. 
This project helps healthcare IT professionals create sample AKTIN CDA documents for testing and development purposes of the AKTIN DWH.
Additional Information can be found on the [Github Wiki](https://github.com/aktin/cda-test-data-generator/wiki).
## Prerequisites

- Python 3.12 (3.11)
- `pip` (Python package installer)

## Installation

1. Clone the repository:
```sh
git clone https://github.com/aktin/cda-test-data-generator
cd cda-test-data-generator
```
2. Install the required Python packages:
```sh
pip install -r requirements.txt
```

## Configuration
The tool requires two main configuration files.

1. Excel Template (`*.xlsx`):
    * Defines the variables and their generation rules
    * Must follow the specified template format (see Documentation)
    * Paths to value sets defined in the Excel must be relative to the Excel file


2. XSLT Template (`*.xslt`):
    * Defines the structure of CDA documents
    * Must be valid XSLT 1.0 or 2.0

These files are already set up in the `/resources` directory by default and ready for use!

More Information can be found on the [Github Wiki/Configuration](https://github.com/aktin/cda-test-data-generator/wiki/Configuration)


## Default Usage
Recommended way to run the tool:
1. Make sure you are in the `/cda-test-data-generator` directory
2. Fill in the parameters as described below
3. Run with filled parameters:
```sh
python src/main.py --number <number_of_CDAs> --xslt <xslt_file> --xlsx <excel_file> [--output <output_dir>][--cleanup]
```
Information on running it in a different directory can be found in the [Github Wiki/How_to_use_it?](https://github.com/aktin/cda-test-data-generator/wiki/How-to-use-it%3F)
### Parameters

| Parameter   | Required | Description                                      | Default                      |
|-------------|----------|--------------------------------------------------|------------------------------|
| `--number`  | Yes | Number of CDA documents to generate              | None                         |
| `--xslt`    | Yes | Absolute/Relative path to XSLT template file     | None                         |
| `--xlsx`    | Yes | Absolute/Relative path to Excel template file    | None                         |
| `--output`  | No | Output directory for CDA files.                  | `<working_directory>` |
| `--cleanup` | No | If cleanup is set, remove intermediate CSV file. |                     |

### Example

To generate 10 CDA files and save them in an output directory, run in the `/cda-test-data-generator` directory:
```sh
python src/main.py --number 10 --xlsx resources/CDAVariables_short.xlsx --xslt resources/EmergencyNote.xslt --output /output
```

## License

This project is licensed under the AGPL-3.0 license.
