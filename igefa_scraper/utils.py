import aiofiles
import json
import os
import pandas as pd
from typing import Dict


async def save_intermediate_data(filename: str, data: Dict):
    """
    Saves data to the intermediate JSONL file.
    Args:
        filename (str): Name of the intermediate file.
        data (Dict): Data to save.
    """
    if data is None:
        return
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, "..", filename)
    filepath = os.path.abspath(filepath)
    async with aiofiles.open(filepath, "a", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False) + "\n")
    print(f"Data saved to {filepath}")


async def load_processed_urls(filename: str) -> set:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, "..", filename)
    filepath = os.path.abspath(filepath)

    if not os.path.exists(filepath):
        print(f"No intermediate file found at {filepath}. Starting fresh.")
        return set()

    processed_urls = set()
    async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
        async for line in f:
            try:
                data = json.loads(line)
                processed_urls.add(data.get("Supplier-URL"))
            except json.JSONDecodeError:
                print(f"Failed to decode line: {line}")
                continue

    print(f"Loaded {len(processed_urls)} processed URLs from {filepath}.")
    return processed_urls


def create_csv(intermediate_file: str, output_file: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    intermediate_path = os.path.join(current_dir, "..", intermediate_file)
    intermediate_path = os.path.abspath(intermediate_path)

    if not os.path.exists(intermediate_path):
        print(f"Intermediate file {intermediate_path} does not exist. Cannot create CSV.")
        return

    data_list = []
    with open(intermediate_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                data_list.append(data)
            except json.JSONDecodeError:
                print(f"Failed to decode line: {line}")
                continue

    if not data_list:
        print("No data found in intermediate file. CSV will not be created.")
        return

    df = pd.DataFrame(data_list)

    # Reorder columns as per requirements
    columns_order = [
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

    # Add missing columns with None values
    for col in columns_order:
        if col not in df.columns:
            df[col] = None

    df = df.reindex(columns=columns_order)

    output_path = os.path.join(current_dir, "..", output_file)
    output_path = os.path.abspath(output_path)

    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"CSV file created successfully at {output_path}.")
