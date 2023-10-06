#!/usr/bin/python3
"""Crawl newegg.com for storage prices."""

import collections
import decimal
import logging
import os
import random
import re
import sys
import time
import typing
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Optional

import daiquiri
import lxml.html
import requests
from jinja2 import Environment, FileSystemLoader

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger(__name__)

# user_agent = 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0'
user_agent = "UniversalFeedParser/5.2.0 +http://feedparser.org/"
product_list_url = "https://www.newegg.com/Product/ProductList.aspx"

re_page = re.compile(r"Page <strong>\d+/(\d+)</strong>")
re_size1 = re.compile(r"\b([0-9.]+) ?([TGtg])[Bb]\b(?!/s)")
re_size2 = re.compile(r"\b([0-9.]+) ?([TGtg])[Bb]?\b(?!/s)")
re_pack = re.compile(r"\b([0-9]+) Pack", re.I)

root_dir = os.path.dirname(sys.argv[0])
data_root = os.path.join(root_dir, "data")


def exists_or_create_dir(d: str) -> None:
    """Create a directory if it doesn't already exist."""
    if not os.path.exists(d):
        os.mkdir(d)


def random_sleep() -> None:
    """Sleep for a random amount of time between 20 and 90 seconds."""
    time.sleep(random.randint(20, 90))


def get_product_list(n: str, page: Optional[int] = None) -> requests.Response:
    """Get product list."""
    params: dict[str, str | int] = {
        "Submit": "ENE",
        "N": n,
        "IsNodeId": 1,
        "ActiveSearchResult": "True",
        "Order": "RELEASE",
        "PageSize": 96,
    }
    if page is not None:
        params["page"] = page
    r = requests.get(
        product_list_url,
        # allow_redirects=False,
        params=params,
        headers={"User-Agent": user_agent},
    )
    print(r.url)
    logger.debug("request", url=r.url)
    return r


# RSS URL: https://www.newegg.com/Product/RSS.aspx?Submit=ENE&N=8000%204814%20600003489&IsNodeId=1&ShowDeactivatedMark=False&Order=RELEASE
# ^ can include order=RELEASE

# seller = newegg: 8000
# condition = new: 4814
# form factor = 2.5": 600003490
# form factor = 3.5": 600003489
# Desktop Internal Hard Drives:  100167523
# Laptop Internal Hard Drives:   100167524
# Desktop External Hard Drives:  100167525
# Portable External Hard Drives: 100167526
# Internal SSD: 100011693
# form factor = 2.5" SSD: 600038463 601330896
# form factor = M.2: 601193224 601193225 601292490
# SATA: 600038506 600038510 600038519
# PCI Express: 600640786 601296941 601301243


filter_params = [
    ("internal_35", '3.5" internal drives', "100167523 8000 4814 600003489"),
    ("internal_25", '2.5" internal drives', "100167523 8000 4814 600003490"),
    ("laptop_25", '2.5" laptop drives', "100167524 8000 4814 600003490"),
    ("portable_25", '2.5" portable drives', "100167526 8000 4818 600003490"),
    # ('portable_35', '3.5" portable drives', '100167526 8000 4818 600003489'),
    ("external_35", '3.5" external drives', "100167525 8000 4818 600003489"),
    (
        "ssd_sata",
        "SSD with SATA interface",
        "100011693 8000 4814 600038506 600038510 600038519",
    ),
    (
        "ssd_pcie",
        "SSD with PCIe interface",
        "100011693 8000 4814 600640786 601296941 601301243",
    ),
]


def page_filename(d: str, name: str, page: int) -> str:
    """Get page filename."""
    return os.path.join(d, f"{name}_page{page:02d}.html")


def save_page(r: requests.models.Response, d: str, name: str, page: int) -> None:
    """Save page."""
    open(page_filename(d, name, page), "w").write(r.text)


def get_pages() -> None:
    """Get pages."""
    today_dir = os.path.join(data_root, str(date.today()))
    exists_or_create_dir(today_dir)

    download = False
    for name, label, filter_param in filter_params:
        filename = page_filename(today_dir, name, 1)
        print(filename)
        if os.path.exists(filename):
            page_content = open(filename).read()
        else:
            logger.info(f"get {name}", label=label, page=1)
            if download:
                random_sleep()
            page1 = get_product_list(filter_param)
            download = True
            page_content = page1.text
            save_page(page1, today_dir, name, 1)
        page_content = page_content.replace("<!-- -->", "")
        page_count = get_page_count(page_content)
        logger.info(f"{name} page count: {page_count}")
        for page_num in range(2, page_count + 1):
            filename = page_filename(today_dir, name, page_num)
            if os.path.exists(filename):
                continue
            logger.info(f"get {name}", label=label, page=page_num)
            if download:
                random_sleep()
            r = get_product_list(filter_param, page=page_num)
            download = True
            save_page(r, today_dir, name, page_num)


def get_page_count(html: str) -> int:
    """Get page count."""
    m = re_page.search(html)
    assert m
    return int(m.group(1))


def hidden_price(item: lxml.html.HtmlElement) -> bool:
    """Hidden price."""
    price_action = item.find('.//li[@class="price-map"]/a')
    hidden = ["See price in cart", "See Price after Checkout"]
    return price_action is not None and price_action.text in hidden


def out_of_stock(item: lxml.html.HtmlElement) -> bool:
    """Item is out of stock."""
    cur_price = item.find('.//li[@class="price-current"]')
    if cur_price is None:
        cur_price = item.find('.//li[@class="price-current "]')
    promo = item.find('.//p[@class="item-promo"]')
    btn_message = item.find('.//span[@class="btn btn-message "]')
    if cur_price is None:
        print(lxml.html.tostring(item, pretty_print=True, encoding="unicode"))
    assert cur_price is not None
    return (
        len(cur_price) == 0
        and (promo is not None and promo.text_content() == "OUT OF STOCK")
        or (btn_message is not None and btn_message.text == "Out Of Stock")
    )


class Item(typing.TypedDict):
    """Item."""

    price: Decimal
    title: str
    size: str
    size_gb: Decimal
    number: str
    price_per_tb: Decimal


def parse_page(filename: str) -> list[Item]:
    """Parse page."""
    root = lxml.html.parse(filename).getroot()

    items: list[Item] = []
    for item in root.xpath("//div[contains(@class, 'item-container')]"):
        title_link = item.find('.//a[@class="item-title"]')
        href = title_link.get("href")
        item_number = href[href.find("Item=") + 5 :]
        title = title_link.text_content()

        #        compare = item.find('.//div[@class="item-compare-box"]//input')
        #        if compare is None:
        #            continue
        #        item_number = compare.get('neg-itemnumber')
        if not item_number:
            print(lxml.html.tostring(item, pretty_print=True, encoding="unicode"))
        assert item_number

        if hidden_price(item) or out_of_stock(item):
            continue
        dollars = item.find('.//li[@class="price-current"]/strong')
        if dollars is not None and dollars.text == "COMING SOON":
            continue
        if dollars is None:
            dollars = item.find('.//li[@class="price-current "]/strong')
        if dollars is None:
            price_was = item.find('.//span[@class="price-was-data"]')
            if price_was is not None:
                continue

        if dollars is None:
            print(item_number, "//", title)
            print(lxml.html.tostring(item, pretty_print=True, encoding="unicode"))
        cents = dollars.getnext()
        price_str = dollars.text + ("" if cents is None else cents.text)
        try:
            price = Decimal(price_str.replace(",", ""))
        except decimal.InvalidOperation:
            print(repr(price_str))
            raise
        m = re_size1.search(title)
        if not m:
            m = re_size2.search(title)
        if not m:
            continue
        size = m.group(1) + m.group(2) + "B"
        size_gb = Decimal(m.group(1))
        if m.group(2) == "T":
            size_gb *= 1000

        items.append(
            {
                "price": price,
                "title": title,
                "size": size,
                "size_gb": size_gb,
                "number": item_number,
                "price_per_tb": (price / size_gb) * 1000,
            }
        )

    return items


def build_file_map(data_dir: str) -> dict[str, list[tuple[int, str]]]:
    """Build file map."""
    files = defaultdict(list)
    for f in sorted(os.listdir(data_dir)):
        pos = f.rfind("_page")
        name = f[:pos]
        page = int(f[pos + 5 : pos + 7])
        files[name].append((page, f))
    return files


def get_data_dir(today: date) -> str:
    """Get data dir."""
    data_dir = os.path.join(data_root, str(today))
    if not os.path.exists(data_dir):
        alt = max(x for x in os.listdir(data_root) if x[0].isdigit())
        print(f"Today dir ({today}) doesn't exist. Using most recent data ({alt}).")
        print()
        data_dir = os.path.join(data_root, alt)
    return data_dir


class Grouped(typing.TypedDict):
    """Grouped items."""

    name: str
    label: str
    items: list[Item]


def group_items(
    today: date,
) -> collections.abc.Iterator[Grouped]:
    """Group items."""
    data_dir = get_data_dir(today)
    files = build_file_map(data_dir)

    for name, label, filter_param in filter_params:
        logger.info(f"category: {label} ({name})")
        seen = set()
        items = []
        for page_num, f in files[name]:
            for item in parse_page(os.path.join(data_dir, f)):
                if item["number"] in seen:
                    logger.info("duplicate", item_number=item["number"])
                    continue
                seen.add(item["number"])
                items.append(item)

        items.sort(key=lambda i: i["price_per_tb"])
        yield {"name": name, "label": label, "items": items}


def build() -> None:
    """Build."""
    build_root = "/var/www/edward/docs/price_per_tb"
    today = date.today()

    templates_dir = os.path.join(root_dir, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))

    data = list(group_items(today))
    index = os.path.join(build_root, "index.html")
    index_template = env.get_template("index.html")
    page = index_template.render(best=data, today=today)
    open(index, "w").write(page)

    list_template = env.get_template("item_list.html")
    for cat in data:
        page = list_template.render(items=cat["items"], today=today, what=cat["label"])
        exists_or_create_dir(os.path.join(build_root, cat["name"]))
        filename = os.path.join(build_root, cat["name"], "index.html")
        open(filename, "w").write(page)


if __name__ == "__main__":
    get_pages()
    build()
