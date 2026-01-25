import asyncio
from playwright.async_api import async_playwright
import json
import os
from amazon import get_product as get_amazon_product
from requests import post

AMAZON = "https://amazon.ca"

URLS = {
    AMAZON: {
        "search_field_query": 'input[name="field-keywords"]',
        "search_button_query": 'input[value="Go"]',
        "product_selector": "div.s-card-container"
    }
}

available_urls = URLS.keys()


def load_auth():
    FILE = os.path.join("Scraper", "auth.json")
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
    product_selector = metadata.get("product_selector")

    if search_field_query and search_button_query:
        print("Filling input field")
        search_box = await page.wait_for_selector(search_field_query, timeout=60000)
        await search_box.fill(search_text)  # Use fill instead of type for better reliability
        print("Pressing search button")
        button = await page.wait_for_selector(search_button_query, timeout=60000)
        
        # Wait for navigation after clicking
        try:
            async with page.expect_navigation(timeout=120000, wait_until="domcontentloaded"):
                await button.click()
        except Exception as e:
            print(f"Navigation timeout or error: {e}")
            # Fallback: wait for load state even if navigation didn't complete
            await page.wait_for_load_state("domcontentloaded", timeout=60000)
        
        print("Waiting for search results to load")
        # Wait for domcontentloaded (more reliable than networkidle for sites like Amazon)
        await page.wait_for_load_state("domcontentloaded", timeout=60000)
        
        # Wait for product selector to ensure results are visible (this is the key indicator)
        if product_selector:
            print("Waiting for product results to appear")
            try:
                await page.wait_for_selector(product_selector, timeout=60000)
                print("Product results found!")
            except Exception as e:
                print(f"Warning: Could not find product selector after 60s: {e}")
                # Try to continue anyway in case selector changed
        else:
            # Give the page a moment to render if no selector provided
            await page.wait_for_timeout(2000)
    else:
        raise Exception("Could not search.")

    return page


async def get_products(page, search_text, selector, get_product): 
    print("Retreiving products.")
    product_divs = await page.query_selector_all(selector)
    print(f"Found {len(product_divs)} product divs")
    words = search_text.split(" ")

    async def process_product(p_div):
        try:
            product = await get_product(p_div)
        except Exception as e:
            return {"_reject_reason": f"exception:{e}"}

        if not product.get("name"):
            product["_reject_reason"] = "missing_name"
            return product
        if not product.get("url"):
            product["_reject_reason"] = "missing_url"
            return product
        if product.get("price") is None:
            product["_reject_reason"] = "missing_price"
            return product

        # Check if all search words are in the product name
        product_name_lower = product["name"].lower()
        all_words_found = all(word.lower() in product_name_lower for word in words if word.strip())
        
        if all_words_found:
            return product
        product["_reject_reason"] = "word_mismatch"
        return product

    # Process all products concurrently
    tasks = [process_product(div) for div in product_divs]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    
    # Build rejection breakdown + keep only accepted products
    reject_counts = {}
    valid_products = []
    for product in results:
        reason = product.get("_reject_reason")
        if reason:
            reject_counts[reason] = reject_counts.get(reason, 0) + 1
            continue
        valid_products.append(product)

    print("Reject breakdown:", reject_counts)
    if valid_products:
        print("Sample accepted product:", {k: valid_products[0].get(k) for k in ("name", "price", "url")})

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
    response = post("http://localhost:5000" + endpoint,
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
        await page.goto(url, timeout=120000)
        print("Loaded initial page.")
        search_page = await search(metadata, page, search_text)

        def func(x): return None
        if url == AMAZON:
            func = get_amazon_product
        else:
            raise Exception('Invalid URL')

        results = await get_products(search_page, search_text, metadata["product_selector"], func)
        print("Saving results. ", results)
        post_results(results, response_route, search_text, url)

        await browser.close()

if __name__ == "__main__":
    # test script
    asyncio.run(main(AMAZON, "ryzen 9 3950x"))
