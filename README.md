# Igefa Scraper

## Description

An asynchronous scraper for collecting product data from the [store.igefa.de](https://store.igefa.de/) website. 
The script saves intermediate data, allowing you to resume work after stopping.


## Contact Information

- **Ім'я:** Oleksii
- **Email:** nick1nick@protonmail.com
- **GitHub:** [alexsproject](https://github.com/alexsproject)

## Requirements

- **Python 3.12+**
- **Poetry**

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/igefa_scraper.git
   cd igefa_scraper
   ```

2. **Install dependencies using Poetry:**

    ```bash
   poetry install
    ```
## Running the Script

1. **Activate the virtual environment:**

    ```bash
    poetry shell
    ```

2. **Run the script:**

   ```bash
   python main.py
   ```
   
## Functionality Description

- Asynchronous Scraping: Utilizes aiohttp and asyncio for efficient data collection.
- Intermediate Datasets: Data is stored in the intermediate_data.jsonl file, allowing you to resume work after stopping.
- CSV Generation: After scraping is complete, an output.csv file is generated with the necessary headers.

## Required Libraries

 - aiohttp
 - aiofiles
 - beautifulsoup4
 - lxml
 - pandas
 - tenacity

## Commands to Run the Project

 - **Run the script:**
   ```bash
   python main.py
   ```
 - **Generate CSV separately:**
   ```bash
   python -c "from igefa_scraper.utils import create_csv; create_csv('intermediate_data.jsonl', 'output.csv')"
   ```

## License
This project is licensed under the MIT License.