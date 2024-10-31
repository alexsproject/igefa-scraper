import asyncio
from igefa_scraper.scraper import IgefaScraper
from igefa_scraper.utils import create_csv
from igefa_scraper.logger import main_logger as logger
import os


async def main():
    async with IgefaScraper() as scraper:
        await scraper.run()

    # Check if the intermediate data file exists
    if os.path.exists(scraper.intermediate_file):
        logger.info(f"Intermediate data file '{scraper.intermediate_file}' found. Creating CSV...")
        create_csv(scraper.intermediate_file, "output.csv")
    else:
        logger.info(f"Intermediate data file '{scraper.intermediate_file}' does not exist. CSV file was not created.")


if __name__ == "__main__":
    asyncio.run(main())
