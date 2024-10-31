import asyncio
import json
import random

import aiohttp
import tenacity
from typing import List

from bs4 import BeautifulSoup

from .parser import extract_products_from_next_data, extract_product_details_from_next_data
from .utils import save_intermediate_data, load_processed_urls
from .constants import BASE_URL, HEADERS
from .logger import main_logger as logger


class IgefaScraper:
    def __init__(self):
        self.session = None
        self.semaphore = asyncio.Semaphore(10)  # Limit the number of concurrent requests
        self.processed_urls = set()
        self.intermediate_file = "intermediate_data.jsonl"

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=HEADERS)
        self.processed_urls = await load_processed_urls(self.intermediate_file)
        logger.info(f"Loaded {len(self.processed_urls)} processed URLs.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(3),
        retry=tenacity.retry_if_exception_type(aiohttp.ClientError),
    )
    async def fetch(self, url: str) -> str:
        async with self.semaphore:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.text()

    async def get_product_urls(self) -> List[str]:
        logger.info("Fetching categories...")
        categories = await self.get_categories()
        logger.info(f"Found {len(categories)} categories.")
        product_urls = []

        tasks = [self.get_products_in_category(category_url) for category_url in categories]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching products in category: {result}")
                continue
            product_urls.extend(result)

        logger.info(f"Total product URLs found: {len(product_urls)}")
        return product_urls

    async def get_categories(self) -> List[str]:
        try:
            html = await self.fetch(BASE_URL)
            soup = BeautifulSoup(html, "lxml")

            category_links = soup.select(
                "div.LYSTypography_color_inherit__25ea4:-soup-contains('Kategorien') + div > div > a"
            )
            logger.info(f"Found {len(category_links)} category links.")

            categories = [BASE_URL + link.get("href") for link in category_links]
            logger.info(f"Processed {len(categories)} category URLs.")
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    async def get_products_in_category(self, category_url: str) -> List[str]:
        logger.info(f"Fetching products in category: {category_url}")
        product_urls = []
        page = 1

        while True:
            page_url = f"{category_url}?page={page}"
            logger.info(f"Fetching page {page} of category: {page_url}")
            try:
                html = await self.fetch(page_url)
                soup = BeautifulSoup(html, "lxml")

                # Find <script id="__NEXT_DATA__"> and extract JSON
                next_data_script = soup.find("script", id="__NEXT_DATA__")
                if not next_data_script:
                    logger.warning(f"Cannot find <script id='__NEXT_DATA__'> on page {page_url}.")
                    break

                next_data_json = next_data_script.string
                if not next_data_json:
                    logger.warning(f"<script id='__NEXT_DATA__'> is empty on page {page_url}.")
                    break

                data = json.loads(next_data_json)
                # Extract products from the page
                products = extract_products_from_next_data(data)
                logger.info(f"Category {category_url}, Page {page}: Found {len(products)} products.")

                if not products:
                    logger.info(f"No products found in category {category_url} on page {page}. Ending pagination.")
                    break

                for product in products:
                    product_url = product.get("Supplier-URL")
                    if product_url and not product_url.startswith("http"):
                        product_url = BASE_URL + product_url
                    if product_url:
                        product_urls.append(product_url)

                # Check if there are more pages
                total = data["props"]["initialProps"]["pageProps"]["initialProductData"].get("total", 0)
                items_per_page = 20  # Assuming 20 products per page
                if total <= page * items_per_page:
                    logger.info(f"No more pages in category {category_url}.")
                    break

                page += 1
            except Exception as e:
                logger.error(f"Error fetching products in category {category_url}, page {page}: {e}")
                break

        logger.info(f"Category {category_url}: Total products found: {len(product_urls)}")
        return product_urls

    async def scrape_product(self, url: str):
        if url in self.processed_urls:
            logger.info(f"Skipping already processed URL: {url}")
            return

        try:
            logger.info(f"Scraping product URL: {url}")
            html = await self.fetch(url)
            soup = BeautifulSoup(html, "lxml")

            # Find <script id="__NEXT_DATA__"> and extract JSON
            next_data_script = soup.find("script", id="__NEXT_DATA__")
            if not next_data_script:
                logger.warning(f"Cannot find <script id='__NEXT_DATA__'> on product page: {url}")
                return
            next_data_json = next_data_script.string
            if not next_data_json:
                logger.warning(f"<script id='__NEXT_DATA__'> is empty on product page: {url}")
                return
            data = json.loads(next_data_json)

            # Extract detailed product information from JSON
            product_data = extract_product_details_from_next_data(data)
            if product_data:
                await save_intermediate_data(self.intermediate_file, product_data)
                self.processed_urls.add(url)
                logger.info(f"Successfully scraped: {url}")
                await asyncio.sleep(random.uniform(0.5, 2.0))  # Delay between requests
            else:
                logger.warning(f"No data scraped for URL: {url}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")

    async def run(self):
        logger.info("Starting scraper...")
        product_urls = await self.get_product_urls()
        logger.info(f"Found {len(product_urls)} product URLs.")

        if not product_urls:
            logger.info("No products found. Exiting scraper.")
            return

        tasks = [self.scrape_product(url) for url in product_urls if url not in self.processed_urls]

        if tasks:
            logger.info(f"Starting to scrape {len(tasks)} products...")
            await asyncio.gather(*tasks)
            logger.info("Scraping completed.")
        else:
            logger.info("No new products to scrape.")
