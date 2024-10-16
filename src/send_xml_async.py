import asyncio
import os
from pathlib import Path
from typing import Dict
import argparse

import aiohttp
import aiofiles
from lxml import etree
import logging

from src import main

# Constants
URL = "http://localhost:5080/aktin/cda/fhir/Binary/$validate"
OUTPUT_DIR = Path(os.environ.get('OUTPUT_DIR', '../output'))
CDA_DIR = OUTPUT_DIR.joinpath('cda')
RESPONSE_DIR = OUTPUT_DIR.joinpath('responses')
FHIR_NAMESPACE = {'f': 'http://hl7.org/fhir'}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def send_xml_file_async(session: aiohttp.ClientSession, input_file: Path, output_file: Path) -> None:
    """
    Asynchronously send an XML file to a server and save the response.

    Args:
        session (aiohttp.ClientSession): The aiohttp session to use for the request.
        input_file (Path): The path to the input XML file.
        output_file (Path): The path where the response should be saved.
    """
    try:
        async with aiofiles.open(input_file, 'rb') as f:
            file_content = await f.read()

        headers = {'Content-Type': 'application/x-cda+xml'}
        async with session.post(URL, data=file_content, headers=headers) as response:
            result = await response.text()
            logger.info(f"Response status for {input_file.name}: {response.status}")
            logger.debug(f"Response content: {result[:100]}...")  # Log first 100 chars

        if result:
            async with aiofiles.open(output_file, 'w') as f:
                await f.write(result)
            logger.info(f"Written response to {output_file}")
        else:
            logger.warning(f"Empty response for {input_file.name}")
    except Exception as e:
        logger.error(f"Error processing {input_file.name}: {str(e)}")


async def process_files_async() -> None:
    """
    Process multiple XML files asynchronously.

    Args:
        num_rows (int, optional): The number of files to process. If None, process all files in the CDA directory.
    """
    RESPONSE_DIR.mkdir(exist_ok=True)

    cda_files = list(CDA_DIR.glob("cda_*.xml"))

    async with aiohttp.ClientSession() as session:
        tasks = [
            send_xml_file_async(
                session,
                cda_file,
                RESPONSE_DIR / f"response_{cda_file.stem.split('_')[1]}.xml"
            )
            for cda_file in cda_files
        ]
        await asyncio.gather(*tasks)


def count_issue_elements(xml_file_path: Path) -> int:
    """
    Count the number of <issue> elements that are children of <OperationOutcome> in an XML file.

    Args:
        xml_file_path (Path): The path to the XML file.

    Returns:
        int: The number of <issue> elements in the XML file.
    """
    try:
        tree = etree.parse(str(xml_file_path))
        return len(tree.xpath('//f:OperationOutcome/f:issue', namespaces=FHIR_NAMESPACE))
    except etree.XMLSyntaxError as e:
        logger.error(f"XML parsing error in {xml_file_path}: {str(e)}")
        return 0


def get_stats() -> Dict[str, int]:
    """
    Analyze the response files and return statistics.

    Returns:
        Dict[str, int]: A dictionary containing the count of correct and error responses.
    """
    stats = {"Correct": 0, "Error": 0}
    issue_cdas = []

    for file in RESPONSE_DIR.glob('*.xml'):
        if count_issue_elements(file) == 1:
            stats["Correct"] += 1
        else:
            stats["Error"] += 1
            issue_cdas.append(file.name)

    logger.info(f"Statistics: {stats}")
    logger.info(f"Files with issues: {issue_cdas}")
    return stats


async def main_async() -> None:
    """
    Main asynchronous function to orchestrate the XML processing and analysis.
    """
    await process_files_async()
    get_stats()


if __name__ == "__main__":
    asyncio.run(main_async())
