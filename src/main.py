import argparse
import glob
import logging
import os

from calculate_dependencies import calculate_dependencies
from csv_to_cda import csv_to_cda
from generate_csv import generate_csv
from src.config import Config


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



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
        generate_csv(config.xlsx, csv_path, n)

        logging.info("Calculating dependencies...")
        calculate_dependencies(csv_path)

        logging.info("Transforming to CDA...")
        csv_to_cda(csv_path, config.xslt, config.output_dir)

        if cleanup:
            clean_up(csv_path)

        logging.info("Processing completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during processing: {str(e)}")
        raise


def main() -> None:
    """Main function to orchestrate the Excel to CDA conversion process."""

    try:
        # Create config at program start
        process_excel_to_cda(config.n, config.cleanup)
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        exit(1)


if __name__ == '__main__':
    setup_logging()
    config = Config.from_args()
    main()
