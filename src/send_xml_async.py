import asyncio
import os

import aiohttp
import logging

from src import main
from lxml import etree

logging.basicConfig(level=logging.INFO)


async def send_xml_file_async(session, url, input_file, output_file):
    try:
        with open(input_file, 'rb') as f:
            file_content = f.read()

        headers = {'Content-Type': 'application/x-cda+xml'}
        async with session.post(url, data=file_content, headers=headers) as response:
            result = await response.text()
            logging.info(f"Response status for {input_file}: {response.status}")
            logging.info(f"Response content: {result[:100]}...")  # Log first 100 chars

        if result:
            with open(output_file, 'w') as f:
                f.write(result)
            logging.info(f"Written response to {output_file}")
        else:
            logging.warning(f"Empty response for {input_file}")
    except Exception as e:
        logging.error(f"Error processing {input_file}: {str(e)}")


async def main_and_send_test_async():
    main.main()
    rows = main.args.n

    output_dir = os.environ['output_dir']
    response_path = os.path.join(output_dir, 'responses')

    if not os.path.isdir(response_path):
        os.mkdir(response_path)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(rows):
            url = "http://localhost:5080/aktin/cda/fhir/Binary/$validate"
            input_file = f"../output/cda/cda_{i + 1}.cda"
            output_file = f"../output/responses/response_{i + 1}.xml"
            task = send_xml_file_async(session, url, input_file, output_file)
            tasks.append(task)

        await asyncio.gather(*tasks)


def count_issue_elements(xml_file_path: str) -> int:
    """
    Count the number of <issue> elements that are children of <OperationOutcome> in an XML file.

    Args:
        xml_file_path (str): The path to the XML file.

    Returns:
        int: The number of <issue> elements in the XML file.
    """
    # Parse the XML file
    tree = etree.parse(xml_file_path)

    # Find all <issue> elements that are children of <OperationOutcome>
    issue_elements = tree.xpath('//f:OperationOutcome/f:issue', namespaces={'f': 'http://hl7.org/fhir'})

    # Return the count of <issue> elements
    return len(issue_elements)


def get_stats():
    order = f"../output/responses/"
    all_files = os.listdir(order)
    stats = {"Correct": 0, "Error": 0}
    issue_cdas = []
    for file in all_files:
        if count_issue_elements(order + file) == 1:
            stats["Correct"] += 1
        else:
            stats["Error"] += 1
            issue_cdas.append(file)

    print(stats)
    print(issue_cdas)


if __name__ == "__main__":
    asyncio.run(main_and_send_test_async())
    get_stats()
