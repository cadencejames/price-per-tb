# HDD/SSD Price Per TB Scraper & Report Generator

This Python script scrapes hard drive (HDD) and solid-state drive (SSD) listings from Amazon, Newegg, and ServerPartDeals. It processes this data to calculate the price per terabyte ($/TB) and generates a self-contained, interactive HTML report designed to be hosted on a static site like GitHub Pages.

The generated HTML report features:
*   Combined listings from all supported retailers.
*   Client-side sorting by Retailer, Product Title, Capacity, Price, and $/TB.
*   Client-side filtering by Retailer.
*   Dark mode toggle.
*   A "Back to Home" link.
*   Status of each scraper run.

**Acknowledgments:**
This project was inspired by and builds upon the functionality of the original Newegg HDD price scraper created by Edward Betts, available at [git.4angle.com/edward/newegg-hdd](https://git.4angle.com/edward/newegg-hdd). This version expands to include multiple retailers and generates a more interactive HTML report.

## Features

*   **Multi-Retailer Scraping:**
    *   Amazon (using `requests` and BeautifulSoup)
    *   Newegg (using Selenium for dynamic content, fetches a single large page)
    *   ServerPartDeals (using Selenium for dynamic content)
*   **Data Processing:** Calculates price per terabyte.
*   **Interactive HTML Report:**
    *   Sortable columns.
    *   Filterable by retailer.
    *   Dark mode support.
    *   Self-contained (all CSS and JavaScript embedded).
*   **Configurable:** Search terms and Amazon page limits can be adjusted in the script.

## Prerequisites

*   Python 3.7+
*   Mozilla Firefox browser installed (for Selenium-based scraping)
*   The following Python libraries:
    *   `requests`
    *   `beautifulsoup4`
    *   `pandas`
    *   `lxml` (recommended parser for BeautifulSoup)
    *   `selenium`
    *   `webdriver-manager` (for automatic GeckoDriver management for Firefox)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/cadencejames/price-per-tb.git
    cd price-per-tb
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies from `requirements.txt`:**
    Ensure you have a `requirements.txt` file in the root of the repository with the following (or similar) content:
    ```
    requests
    beautifulsoup4
    pandas
    lxml
    selenium
    webdriver-manager
    ```
    Then, install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Open the Python script (e.g., `hdd_price_scraper.py`) and modify these variables at the top if needed:

*   `SEARCH_TERM`: The default search query used for Amazon and Newegg (e.g., "internal hard drive", "nvme ssd").
*   `MAX_PAGES_PER_SITE`: How many pages of Amazon search results to scrape. Newegg and ServerPartDeals use different mechanisms.
*   `MIN_DELAY_S`, `MAX_DELAY_S`: Delays between requests to be polite to servers.
*   `HEADERS`: This dictionary contains HTTP headers sent with requests, most notably the `User-Agent`.
    *   The script includes a default, common User-Agent.
    *   For potentially better results or to reduce using a shared default, you can update the `'User-Agent'` value with your own browser's current string. To find it, simply search "my user agent" in your web browser (e.g., on DuckDuckGo, Google) and copy the result.
    *   Periodically updating the User-Agent to a more recent one can be beneficial.
*   `output_dir`: The directory where the report will be saved (default: `pages`).
*   `html_output_filename`: The name of the generated HTML file (default: `hdd_prices_report.html` inside `output_dir`).
*   **"Back to Home" Link:** Inside the `html_content` f-string within the `if __name__ == "__main__":` block, the link is set to `href="/"`. This should work if your site's homepage is at the root of the domain (e.g., `yourdomain.com/`). If your GitHub Pages site is served from a subdirectory (e.g., `username.github.io/price-per-tb/`), you may need to change this to `href="/price-per-tb/"`.

## Usage

1.  Ensure all prerequisites are installed and Firefox is available.
2.  Navigate to the directory containing the script.
3.  Run the script from your terminal:
    ```bash
    python hdd_price_scraper.py
    ```
    *(Replace `hdd_price_scraper.py` with your actual script filename if different.)*

4.  The script will:
    *   Log its progress to the console.
    *   Attempt to scrape data from Amazon, Newegg, and ServerPartDeals.
    *   Generate an HTML file at `pages/hdd_prices_report.html` (or your configured path).

5.  Open the generated `pages/hdd_prices_report.html` file in your web browser to view the interactive report.

6.  **For GitHub Pages Deployment:**
    *   Ensure the Python script is run (e.g., locally or via a GitHub Action) and the `pages/hdd_prices_report.html` file is generated.
    *   Commit and push the `pages/hdd_prices_report.html` file (and the `pages` directory if it's new) to your `price-per-tb` repository.
    *   Ensure your GitHub Pages site is configured to build from the correct branch (e.g., `main` or `gh-pages`).
    *   You can then link to this page from your site's navigation.

## How it Works

*   **Amazon:** Uses the `requests` library to fetch HTML and `BeautifulSoup4` to parse product listings.
*   **Newegg & ServerPartDeals:** Employs `Selenium` with `webdriver-manager` to control a headless Firefox browser. This handles JavaScript-heavy pages.
    *   For Newegg, it requests a single large page of results (`PageSize=96`).
    *   For ServerPartDeals, it loads the specified collection page and uses scrolling.
*   **Data Processing:** `pandas` structures the scraped data and calculates 'Price per TB'.
*   **HTML Report Generation:** The script constructs a full HTML document with embedded CSS for styling (including dark mode and table layout) and JavaScript for client-side sorting, filtering, and theme toggling.

## Troubleshooting & Notes

*   **Web Scraping Fragility:** Website HTML structures change. If scraping fails for a retailer, CSS selectors in the corresponding `scrape_...()` function likely need updating.
*   **Anti-Bot Measures:** Retailers may block scrapers. If issues persist, try updating the `HEADERS` User-Agent, ensure delays are adequate, or investigate more advanced anti-detection techniques (which can be complex).
*   **Selenium Driver:** `webdriver-manager` handles GeckoDriver for Firefox. Ensure Firefox is updated.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
