import argparse
import glob
import logging
import os
from typing import List, Tuple

import toml

from calculate_dependencies import calculate_dependencies
from csv_to_cda import csv_to_cda
from generate_csv import generate_csv

# Constants
ENV_VARS: List[Tuple[str, str]] = [
    ('CSV_PATH', 'cda_paths.csv_path'),
    ('EXCEL_PATH', 'cda_paths.excel_path'),
    ('XSLT_FILE', 'cda_paths.xslt_file'),
    ('OUTPUT_DIR', 'cda_paths.output_dir'),
    ('CLINICS_CSV', 'csv_paths.clinics_csv'),
    ('DIAGNOSES_CSV', 'csv_paths.diagnoses_csv'),
    ('CEDIS_CSV', 'csv_paths.cedis_csv'),
    ('INDIVIDUAL_ATTRIBUTES_CSV', 'csv_paths.individual_attributes_csv'),
]


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def set_environment_variables(config_path: str) -> None:
    """
    Set environment variables based on the provided configuration file.

    Args:
        config_path (str): Path to the configuration file.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        toml.TomlDecodeError: If the configuration file is not valid TOML.
    """
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(config_path)))

        with open(config_path, 'r') as file:
            config = toml.load(file)

        for section in ['cda_paths', 'csv_paths']:
            for key in config[section]:
                config[section][key] = resolve_path(base_path, config[section][key])

        for env_var, config_key in ENV_VARS:
            section, key = config_key.split('.')
            os.environ[env_var] = config[section][key]

        logging.info("Environment variables set successfully.")
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        raise
    except toml.TomlDecodeError:
        logging.error(f"Invalid TOML file: {config_path}")
        raise


def parse_command_line() -> Tuple[int, str, bool]:
    """
    Parse command line arguments.

    Returns:
        Tuple[int, str, bool]: Number of patients, config file path, and cleanup flag.
    """
    parser = argparse.ArgumentParser(description='Process Excel to CDA.')
    parser.add_argument('--n', type=int, required=True, help='Number of patients to generate.')
    parser.add_argument('--config', type=str, required=True, help='Filepath for configuration TOML file.')
    parser.add_argument('--cleanup', action='store_true', help='Remove intermediate CSV file after processing.')
    args = parser.parse_args()
    return args.n, args.config, args.cleanup


def resolve_path(base_path: str, relative_path: str) -> str:
    """
    Resolve relative path to absolute path.

    Args:
        base_path (str): Base directory path.
        relative_path (str): Relative path to resolve.

    Returns:
        str: Absolute path.
    """
    return os.path.abspath(os.path.join(base_path, relative_path))


def process_excel_to_cda(n: int, cleanup: bool) -> None:
    """
    Process Excel file to CDA.

    Args:
        n (int): Number of patients to generate.
        cleanup (bool): Whether to remove the intermediate CSV file.
    """
    csv_path = os.environ['CSV_PATH']
    excel_path = os.environ['EXCEL_PATH']
    xslt_file = os.environ['XSLT_FILE']

    try:
        logging.info("Generating CSV...")
        generate_csv(excel_path, csv_path, n)

        logging.info("Calculating dependencies...")
        calculate_dependencies(csv_path)

        logging.info("Transforming to CDA...")
        csv_to_cda(csv_path, xslt_file)

        if cleanup:
            logging.info("Cleaning up intermediate CSV file...")
            os.remove(csv_path)

            logging.info("Cleaning up intermediate RAW files")
            # Remove all files in the raw directory
            raw_dir = os.path.join(os.environ['OUTPUT_DIR'], 'raw')
            for file_path in glob.glob(os.path.join(raw_dir, '*')):
                os.remove(file_path)

        logging.info("Processing completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during processing: {str(e)}")
        raise


def main() -> None:
    """Main function to orchestrate the Excel to CDA conversion process."""
    setup_logging()

    try:
        n, config, cleanup = parse_command_line()
        set_environment_variables(config)
        process_excel_to_cda(n, cleanup)
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()