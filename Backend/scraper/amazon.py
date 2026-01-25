from asyncio import gather


def _parse_price(text: str):
    if not text:
        return None
    cleaned = (
        text.replace("$", "")
        .replace(",", "")
        .replace("\u00a0", " ")
        .strip()
    )
    try:
        return float(cleaned)
    except Exception:
        return None


def _normalize_amazon_url(href: str):
    if not href:
        return None
    href = href.strip()
    if not href:
        return None
    if href.startswith("http"):
        return href.split("?")[0]
    return f"https://www.amazon.ca{href.split('?')[0]}"


async def get_stock(product_div):
    elements = await product_div.query_selector_all('.a-size-base')
    filtered_elements = [element for element in elements if 'stock' in await element.inner_text()]
    return filtered_elements


async def get_product(product_div):
    # Query for all elements at once
    image_element_future = product_div.query_selector('img.s-image')
    # Name selectors vary across Amazon layouts/experiments; we’ll try several below
    name_element_future = product_div.query_selector('h2 a span')
    # Prefer the real price container; Amazon search cards include many `.a-offscreen` spans (e.g. "8 sizes")
    price_element_future = product_div.query_selector('span.a-price span.a-offscreen')
    # Prefer the title link; the previous selector was too specific and often returned None
    url_element_future = product_div.query_selector('a[href*="/dp/"]')

    # Await all queries at once
    image_element, name_element, price_element, url_element = await gather(
        image_element_future,
        name_element_future,
        price_element_future,
        url_element_future,
        # get_stock(product_div)
    )

    # Fetch all attributes and text at once
    image_url = await image_element.get_attribute('src') if image_element else None
    product_name = (await name_element.inner_text()).strip() if name_element else None
    if not product_name:
        # Fallback selectors for title text (common on Amazon search result cards)
        for sel in (
            'span.a-size-base-plus.a-color-base.a-text-normal',
            'span.a-size-medium.a-color-base.a-text-normal',
            'h2 span',
            'h2',
        ):
            el = await product_div.query_selector(sel)
            if el:
                txt = (await el.inner_text()).strip()
                if txt:
                    product_name = txt
                    break
    product_price = None
    if price_element:
        product_price = _parse_price(await price_element.inner_text())
    else:
        # Fallback: try any `.a-offscreen` within the card and pick the first parseable value
        for el in await product_div.query_selector_all('span.a-offscreen'):
            price = _parse_price(await el.inner_text())
            if price is not None:
                product_price = price
                break
    product_url = None
    href = None
    if url_element:
        href = await url_element.get_attribute('href')

    # Fallback: scan all anchors in the card and pick the best candidate
    if not href:
        for a in await product_div.query_selector_all('a[href]'):
            cand = await a.get_attribute('href')
            if not cand:
                continue
            # Prefer canonical product links
            if "/dp/" in cand:
                href = cand
                break
            if href is None:
                href = cand

    product_url = _normalize_amazon_url(href)
    # stock = stock_element[0] if len(stock_element) > 0 else None

    return {"img": image_url, "name": product_name, "price": product_price, "url": product_url}
