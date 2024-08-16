import asyncio
import aiohttp
import logging

from src import main

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
    rows = main.args.rows

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(rows):
            url = "http://localhost:5080/aktin/cda/fhir/Binary/$validate"
            input_file = f"../output/cda/cda_{i + 1}.cda"
            output_file = f"../output/fehlercodes/response_{i + 1}.xml"
            task = send_xml_file_async(session, url, input_file, output_file)
            tasks.append(task)

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main_and_send_test_async())
