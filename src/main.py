import glob
import logging
import os

from calculate_dependencies import calculate_dependencies
from csv_to_cda import csv_to_cda
from generate_csv import generate_csv
from config import config


def setup_logging() -> None:
    """
    Set up logging configuration.

    This function configures the logging module to output messages with a specific format and at the INFO level.
    """
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


def clean_up(csv_path: str) -> None:
    """
    Clean up intermediate files including the specified CSV file

    Args:
        csv_path (str): The path to the intermediate CSV file to be removed.
    """
    logging.info("Cleaning up intermediate CSV file...")
    os.remove(csv_path)
    logging.info("Cleaning up intermediate RAW files")



def process_excel_to_cda(number: int, cleanup: bool, output_dir: str) -> None:
    """
    Process Excel file to CDA format.

    This function orchestrates the conversion of an Excel file to CDA format by generating a CSV file,
    calculating dependencies, and transforming the CSV to CDA. Optionally, it cleans up intermediate files.

    Args:
        number (int): Number of rows to process from the Excel file.
        cleanup (bool): Flag to indicate whether to clean up intermediate files.
        output_dir (str, optional): Directory to store output files. Defaults to '../output/'.
    """
    # Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_path = os.path.join(output_dir, "data.csv")

    try:
        logging.info("Generating CSV...")
        generate_csv(config.xlsx, csv_path, number)

        logging.info("Calculating dependencies...")
        calculate_dependencies(csv_path)

        logging.info("Transforming to CDA...")
        csv_to_cda(csv_path, config.xslt, config.output)

        if cleanup:
            clean_up(csv_path)

        logging.info("Processing completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during processing: {str(e)}")
        raise


def main() -> None:
    """
    Main function to orchestrate the Excel to CDA conversion process.

    This function sets up logging and initiates the processing of the Excel file to CDA format.
    """
    try:
        # Create config at program start
        process_excel_to_cda(config.number, config.cleanup, config.output)
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        exit(1)


if __name__ == '__main__':
    setup_logging()
    main()