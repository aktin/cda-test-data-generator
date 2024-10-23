import argparse
import glob
import logging
import os

from calculate_dependencies import calculate_dependencies
from csv_to_cda import csv_to_cda
from generate_csv import generate_csv


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_command_line() -> None:
    """
    Parse command line arguments.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(prog='cda-test-data-generator', description='Process Excel to CDA.')
    parser.add_argument('--n', type=int, required=True, help='Number of patients to generate.')
    parser.add_argument('--cleanup', action='store_true', help='Remove intermediate CSV file after processing.')
    parser.add_argument('--xlsx', type=str, required=True, help='Filepath to the input Excel file.')
    parser.add_argument('--xslt', type=str, required=True, help='Filepath to the input XSLT file.')
    parser.add_argument('--o', type=str, required=False, default='../output/',
                        help='Output directory for generated files.')  # noqa E501
    parser.parse_args(namespace=main)


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


def clean_up(csv_path):
    """
    Clean up intermediate files including the specified CSV file and all files in the raw directory.

    Args:
        csv_path (str): The path to the intermediate CSV file to be removed.
    """
    logging.info("Cleaning up intermediate CSV file...")
    os.remove(csv_path)
    logging.info("Cleaning up intermediate RAW files")
    # Remove all files in the raw directory
    raw_dir = os.path.join(os.environ['OUTPUT_DIR'], 'raw')
    for file_path in glob.glob(os.path.join(raw_dir, '*')):
        os.remove(file_path)


def process_excel_to_cda(n: int, cleanup: bool, output_dir='../output/') -> None:
    # Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_path = os.path.join(output_dir, "data.csv")

    try:
        logging.info("Generating CSV...")
        generate_csv(main.xlsx, csv_path, n)

        logging.info("Calculating dependencies...")
        calculate_dependencies(csv_path)

        logging.info("Transforming to CDA...")
        csv_to_cda(csv_path, main.xslt, main.o)

        if cleanup:
            clean_up(csv_path)

        logging.info("Processing completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during processing: {str(e)}")
        raise


def main() -> None:
    """Main function to orchestrate the Excel to CDA conversion process."""
    setup_logging()

    try:
        parse_command_line()
        process_excel_to_cda(main.n, main.cleanup)
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()
