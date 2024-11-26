import asyncio
from playwright.async_api import async_playwright
import json
import os
from amazon import get_product as get_amazon_product
from requests import post
from playwright._impl._errors import Error
import asyncio
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

AMAZON = "https://amazon.ca"
URL = os.getenv("REACT_APP_API_URL", "http://localhost:5000");

URLS = {
    AMAZON: {
        "search_field_query": 'input[name="field-keywords"]',
        "search_button_query": 'input[value="Go"]',
        "product_selector": "div.s-card-container"
    }
}

available_urls = URLS.keys()


def load_auth():
    FILE = os.path.join("temp", "auth.json")
    with open(FILE, "r") as f:
        return json.load(f)

# place your bright data credentials in auth.json file with keys: "username", "password" and "host"
cred = load_auth()
auth = f'{cred["username"]}:{cred["password"]}'
browser_url = f'wss://{auth}@{cred["host"]}'


async def search(metadata, page, search_text):
    print(f"Searching for {search_text} on {page.url}")
    search_field_query = metadata.get("search_field_query")
    search_button_query = metadata.get("search_button_query")

    if search_field_query and search_button_query:
        print("Filling input field")
        search_box = await page.wait_for_selector(search_field_query)
        await search_box.type(search_text)
        print("Pressing search button")
        button = await page.wait_for_selector(search_button_query)
        await button.click()
    else:
        raise Exception("Could not search.")

    await page.wait_for_load_state()
    return page


async def get_products(page, search_text, selector, get_product):
    print("Retreiving products.")
    product_divs = await page.query_selector_all(selector)
    valid_products = []
    words = search_text.split(" ")

    async def process_product(div):
        product = await get_product(div)
        if not product["price"] or not product["url"]:
            return
        for word in words:
            if not product["name"] or word.lower() not in product["name"].lower():
                break
        else:
            valid_products.append(product)

    tasks = [process_product(div) for div in product_divs]

    await asyncio.gather(*tasks)
    return valid_products


def save_results(results):
    data = {"results": results}
    FILE = os.path.join("Scraper", "results.json")
    with open(FILE, "w") as f:
        json.dump(data, f)


def post_results(results, endpoint, search_text, source):
    headers = {
        "Content-Type": "application/json"
    }
    data = {"data": results, "search_text": search_text, "source": source}

    print("Sending request to", endpoint)
    response = post(URL + endpoint,
                    headers=headers, json=data)
    print("Status code:", response.status_code)


async def main(url, search_text, response_route):
    metadata = URLS.get(url)
    if not metadata:
        print("Invalid URL.")
        return

    async with async_playwright() as pw:
        print('Connecting to browser.')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        page = await browser.new_page()
        print("Connected.")
        retries = 3  # Define the number of retries
        for attempt in range(retries):
            try:
                if "www." not in url:
                    url = url.replace("amazon.ca", "www.amazon.ca")
                await page.goto(url, timeout=60000)
                await page.wait_for_selector(metadata.get("search_field_query"), timeout=60000)
                break
            except Error as e:
                # If navigation fails, retry (up to 3 attempts)
                if attempt < retries - 1:
                    print(f"Retrying navigation (attempt {attempt + 1})...")
                    await asyncio.sleep(2)
                    continue
                else:
                    print(f"Navigation error: {e}")
                    raise e  # Raise the error if all retries fail
        print("Loaded initial page.")
        search_page = await search(metadata, page, search_text)

        def func(x): return None
        if urlparse(url).netloc.replace("www.", "") == urlparse(AMAZON).netloc:
            func = get_amazon_product
        else:
            raise Exception('Invalid URL')

        results = await get_products(search_page, search_text, metadata["product_selector"], func)
        print("Saving results.")
        post_results(results, response_route, search_text, url)

        await browser.close()

if __name__ == "__main__":
    # test script
    asyncio.run(main(AMAZON, "ryzen 9 3950x"))
