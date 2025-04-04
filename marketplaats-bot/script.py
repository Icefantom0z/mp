import httpx
from db import DB
import time
import schedule
import os
from webhook import notify_from_webhook


def is_first_run() -> bool:
    try:
        with open("runcounter.txt", "r") as f:
            data = f.read()
            if data:
                return False

    except IOError:
        with open("runcounter.txt", "w") as f:
            f.write("1")
        return True


FIRST_RUN = is_first_run()
print(f"FIRST_RUN IS {FIRST_RUN}")

d = DB(os.environ.get("DB_PATH") or "../data/test.db")

if FIRST_RUN:
    d.init()


def create_query_url(query: str):
    url_string = f"https://www.marktplaats.nl/lrp/api/search?attributesByKey[]=offeredSince%3AVandaag&limit=30&offset=0&query={query}&searchInTitleAndDescription=true&sortBy=SORT_INDEX&sortOrder=DECREASING&viewOptions=list-view"

    return url_string


def insert_keyword(keyword: str) -> bool:
    res = d.insert_keyword(keyword)
    return res


def delete_keyword(keyword: str) -> bool:
    res = d.delete_keyword(keyword=keyword)
    return res


def fetch_all_keywords() -> list:
    keywords = d.fetch_keywords()
    return keywords


def create_all_query_urls() -> dict:
    query_urls = {}

    keywords = fetch_all_keywords()
    if keywords:
        for row in keywords:
            keyword = row["keyword"]
            query_urls[keyword] = create_query_url(keyword)

    return query_urls


def make_request_or_log(url) -> httpx.Response:
    try:
        r = httpx.get(url)
        return r
    except httpx.RequestError as e:
        print(e)


def check_for_new_listings():
    query_urls = create_all_query_urls()

    for query in query_urls:
        current_listings = d.fetch_all_listings(query=query)
        is_empty = len(current_listings) == 0

        print(f"checking for new listings for {query}\n")
        # r = httpx.get(query_urls[query])
        r = make_request_or_log(query_urls[query])

        if not r:
            return
        else:
            data = r.json()

        print(f"collected data for {len(data['listings'])} entries")

        for item in data["listings"]:

            item_id = item.get("itemId")
            item_title = item.get("title")
            item_url = item.get("vipUrl")
            item_keyword = query

            item_price = item.get("priceInfo").get("priceCents")
            try:
                item_image = item.get("pictures")[0].get("mediumUrl", "not available")
            except Exception:
                item_image = "https://placehold.co/600x400"

            item_price = (
                int(item_price) / 100 if (type(item_price) == int) else "not available"
            )

            insert_time = int(time.time())

            obj = {
                "listing_id": item_id,
                "listing_title": item_title,
                "listing_vip_url": item_url,
                "listing_keyword": item_keyword,
                "tstep": insert_time,
            }

            res = d.insert_listing(obj)

            print(f"DB is empty: {is_empty}")

            if res and not is_empty:
                notify_from_webhook(
                    obj.get("listing_id"),
                    obj.get("listing_title"),
                    obj.get("listing_vip_url"),
                    obj.get("listing_keyword"),
                    item_price,
                    item_image,
                )


if __name__ == "__main__":
    schedule.every(2).minutes.do(check_for_new_listings)

    print("checking for new updates every 2 minutes")

    while True:
        schedule.run_pending()
        time.sleep(1)
