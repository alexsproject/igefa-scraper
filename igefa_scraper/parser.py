from typing import List, Dict, Optional

from .constants import BASE_URL
from .logger import main_logger as logger


def extract_products_from_next_data(data: dict) -> List[Dict]:
    """
    Extracts a list of products from the JSON data of a category page.
    Args:
        data (dict): JSON data from the category page.
    Returns:
        List[Dict]: List of product dictionaries.
    """
    products = []
    try:
        hits = data["props"]["initialProps"]["pageProps"]["initialProductData"]["hits"]
        for hit in hits:
            if not hit:
                continue  # Skip empty records

            main_variant = hit.get("mainVariant")
            if not main_variant:
                continue  # Skip if mainVariant is missing or None

            slug = main_variant.get("slug")
            if not slug:
                continue  # Skip if slug is missing

            product_id = main_variant.get("id")
            if not product_id:
                continue

            product_url = f"{BASE_URL}/p/{slug}/{product_id}"

            product = {
                "Supplier-URL": product_url,
            }
            products.append(product)
    except KeyError as e:
        logger.info(f"KeyError extracting products from category JSON: {e}")
    except Exception as e:
        logger.info(f"Error extracting products from category JSON: {e}")
    return products


def extract_product_details_from_next_data(data: dict) -> Optional[Dict]:
    """
    Extracts detailed product information from the JSON data of a product page.
    Args:
        data (dict): JSON data from the product page.
    Returns:
        Optional[Dict]: Dictionary of product details, or None if extraction fails.
    """
    try:
        product = data["props"]["initialProps"]["pageProps"]["product"]
        if not product:
            logger.info("Hit is empty in product JSON data.")
            return None

        main_variant = product.get("mainVariant")
        if not main_variant:
            logger.info("mainVariant is missing or None in product JSON data.")
            return None

        slug = main_variant.get("slug")
        if not slug:
            logger.info("slug is missing in mainVariant.")
            return None

        product_id = main_variant.get("id")
        if not product_id:
            logger.info("id is missing in mainVariant.")
            return None

        product_url = f"{BASE_URL}/p/{slug}/{product_id}"

        # Extract breadcrumbs from 'breadcrumbs' -> 'hierarchy'
        breadcrumbs = product.get("breadcrumbs", {}).get("hierarchy", [])
        breadcrumb_names = [item.get("slug", "").strip() for item in breadcrumbs if item.get("slug")]
        breadcrumb_str = "/".join(breadcrumb_names)

        # Get the description from mainVariant
        description = main_variant.get("description", "").strip()

        # Extract part before '---' for Add. Description and part after '---' for Product Description
        if "---" in description:
            parts = description.split("---")
            add_description = parts[0].strip()
            product_description = parts[1].strip() if len(parts) > 1 else ""
        else:
            add_description = ""
            product_description = description

        # Extract Product Image URL from mainVariant['images']
        images = main_variant.get("images", [])
        if images:
            product_image_url = images[0].get("url", "").strip()
        else:
            product_image_url = ""

        # Extract 'Manufacturer' from 'hit' -> 'brand'
        manufacturer_current = product.get("brand", {}).get("name", "").strip()
        logger.debug(f"Manufacturer from brand: '{manufacturer_current}'")

        # Extract 'Manufacturer' from 'clientFields' -> 'attributes'
        manufacturer_attribute = ""
        attributes = product.get("clientFields", {}).get("attributes", [])
        if not isinstance(attributes, list):
            logger.warning("'attributes' is not a list in clientFields.")
            attributes = []

        for attribute in attributes:
            if attribute and attribute.get("label") == "Hersteller":
                manufacturer_attribute = attribute.get("value", "").strip()
                logger.debug(f"Manufacturer from attributes: '{manufacturer_attribute}'")
                break  # Stop after finding the first matching 'Hersteller'

        # Use 'manufacturer_current' if available, else 'manufacturer_attribute'
        manufacturer = manufacturer_current if manufacturer_current else manufacturer_attribute
        logger.debug(f"Final Manufacturer: '{manufacturer}'")

        product_data = {
            "Product Name": product.get("name", ""),
            "Original Data Column 1 (Breadcrumb)": breadcrumb_str,
            "Original Data Column 2 (Ausführung)": product.get("variationName", ""),
            "Supplier Article Number": product.get("sku", ""),
            "EAN/GTIN": main_variant.get("gtin", ""),
            "Article Number": product.get("skuProvidedBySupplier", ""),
            "Product Description": product_description,
            "Supplier": "igefa Handelsgesellschaft",
            "Supplier-URL": product_url,
            "Product Image URL": product_image_url,
            "Manufacturer": manufacturer or '',
            "Original Data Column 3 (Add. Description)": add_description,
        }
        return product_data
    except KeyError as e:
        logger.info(f"KeyError extracting product details: {e}")
        return None
    except Exception as e:
        logger.info(f"Error extracting product details: {e}")
        return None
