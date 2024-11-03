import asyncio
import json
from bs4 import BeautifulSoup
import aiohttp
import pytest

from igefa_scraper.parser import extract_product_details_from_next_data


@pytest.mark.asyncio
async def test_parse_product_details_live():
    product_url = ("https://store.igefa.de/p/clean-and-clever-smartline-seifencr-me-ros-sma-91-1-"
                   "sma91-1-seifencreme-12x500ml/k9UiS8fZKdKxrhxcZGuqx7")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(product_url) as response:
                assert response.status == 200, f"Failed to fetch the product page, status code: {response.status}"
                html = await response.text()
        except aiohttp.ClientError as e:
            pytest.fail(f"HTTP request failed: {e}")

    soup = BeautifulSoup(html, "lxml")
    next_data_script = soup.find("script", id="__NEXT_DATA__")

    assert next_data_script is not None, "Cannot find <script id='__NEXT_DATA__'> in the product page."

    try:
        data = json.loads(next_data_script.string)
    except json.JSONDecodeError as e:
        pytest.fail(f"JSON decode error: {e}")

    product_data = extract_product_details_from_next_data(data)

    assert product_data is not None, "No data scraped from the product page."

    expected_keys = [
        "Product Name",
        "Original Data Column 1 (Breadcrumb)",
        "Original Data Column 2 (Ausführung)",
        "Supplier Article Number",
        "EAN/GTIN",
        "Article Number",
        "Product Description",
        "Supplier",
        "Supplier-URL",
        "Product Image URL",
        "Manufacturer",
        "Original Data Column 3 (Add. Description)",
    ]

    for key in expected_keys:
        assert key in product_data, f"'{key}' is missing in product_data"

    assert product_data["Supplier"] == "igefa Handelsgesellschaft", "Incorrect Supplier value"

    assert (
        isinstance(product_data["Product Name"], str) and product_data["Product Name"]
    ), "Kolibri Comface Mundschutz 3-lagig Typ IIR"
    assert isinstance(product_data["EAN/GTIN"], str) and product_data["EAN/GTIN"], "4024009029110"
