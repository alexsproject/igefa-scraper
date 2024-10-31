from igefa_scraper.parser import extract_product_details_from_next_data
from bs4 import BeautifulSoup
import json


def test_parse_product_details():
    try:
        with open("test_category_data.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print("Test HTML file not found: test_category_data.html")
        return

    soup = BeautifulSoup(html, "lxml")
    next_data_script = soup.find("script", id="__NEXT_DATA__")
    if not next_data_script:
        print("Cannot find <script id='__NEXT_DATA__'> in test_category_data.html")
        return

    try:
        data = json.loads(next_data_script.string)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return

    product_data = extract_product_details_from_next_data(data)
    if product_data:
        print("Successfully scraped")
        for key, value in product_data.items():
            print(f"{key}: {value}")
    else:
        print("No data scraped")


if __name__ == "__main__":
    test_parse_product_details()
