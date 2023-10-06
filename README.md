# Newegg hard drive price tracker

## Overview

The Newegg hard drive price tracker is a Python tool designed to fetch the prices of various types of hard drives from Newegg's online store. It sorts and displays these drives based on their price per terabyte, making it easier for users to find the most cost-effective storage solutions. The output is available at the [Price per TB](https://edwardbetts.com/price_per_tb/) page.

## Requirements

- Python 3.x
- `requests`
- `lxml`
- `jinja2`
- `daiquiri`

## Files in the Repository

- `crawl.py`: The main script that crawls Newegg's product listings and extracts relevant data.
- `README.md`: This file, which provides an overview and instructions for the tool.

## Installation

1. Clone the repository:

    ```bash
    git clone https://git.4angle.com/edward/newegg-hdd.git
    ```

2. Change into the project directory:

    ```bash
    cd newegg-hdd
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Automated Crawling

You can set up a cron job to automate the data crawling process. The cron job will execute the `crawl.py` script daily at 08:50. Below is the crontab configuration:

```
50 08 * * * chronic ~/src/newegg-hdd/crawl.py
```

### Manual Crawling

Run the `crawl.py` script manually:

```bash
python crawl.py
```

### Output

After the script runs, you can view the sorted listings at the [Price per TB](https://edwardbetts.com/price_per_tb/) page.

## Functionality

The tool performs the following operations:

- Crawls the Newegg product listings based on predefined filter parameters.
- Downloads and saves HTML pages for later parsing.
- Extracts relevant details, such as price, size, and product number.
- Calculates the price per terabyte for each hard drive.
- Outputs a sorted list of hard drives based on their price per terabyte.

## License

This tool is released under the [MIT License](LICENSE).

## Contributing

If you find any bugs or have suggestions for improvements, please open an issue on the repository.

## Contact

For any queries or issues, please visit the repository at [https://git.4angle.com/edward/newegg-hdd](https://git.4angle.com/edward/newegg-hdd).
