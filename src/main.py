import os
import toml
import argparse

from generate_csv import generate_csv
from csv_to_cda import csv_to_cda
from calculate_dependencies import calculate_dependencies


def set_environment_variables(config):
    """
    Set environment variables based on the provided configuration dictionary.

    Args:
        config (dict): Configuration dictionary containing paths for environment variables.

    Returns:
        None
    """
    env_vars = [
        ('CSV_PATH', 'cda_paths.csv_path'),
        ('EXCEL_PATH', 'cda_paths.excel_path'),
        ('XSLT_FILE', 'cda_paths.xslt_file'),
        ('OUTPUT_DIR', 'cda_paths.output_dir'),
        ('CITIES_CSV', 'csv_paths.cities_csv'),
        ('DIAGNOSES_CSV', 'csv_paths.diagnoses_csv'),
        ('CEDIS_CSV', 'csv_paths.cedis_csv')
    ]

    for env_var, config_key in env_vars:
        section, key = config_key.split('.')
        os.environ[env_var] = config[section][key]


def parse_command_line():
    global parser, args, n
    parser = argparse.ArgumentParser(description='Process Excel to CDA.')
    parser.add_argument('--n', type=int, required=True, help='Number of patients to generate.')
    args = parser.parse_args()
    n = args.n


def main():
    config = toml.load('../config.toml')

    set_environment_variables(config)

    parse_command_line()

    csv_path = os.environ['CSV_PATH']
    excel_path = os.environ['EXCEL_PATH']
    xslt_file = os.environ['XSLT_FILE']

    # First step: Generate csv with rows as patients
    generate_csv(excel_path, csv_path, n)

    # Second step: Set dependable variables
    calculate_dependencies(csv_path)

    # Third step: Transform to CDA
    csv_to_cda(csv_path, xslt_file)

    # Remove data.csv
    # os.remove(csv_path)


if __name__ == '__main__':
    main()
