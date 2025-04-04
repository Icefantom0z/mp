import httpx
import os
import logging
from dotenv import load_dotenv

load_dotenv()

webhook_urls = os.environ.get("WEBHOOK_URL").split(",")

if os.environ.get("ENV") == "dev":
    webhook_urls = webhook_urls[1]

print([webhook_urls])

mk_url = "https://www.marktplaats.nl"


def notify_from_webhook(id, title, vipUrl, keyword, price: str, image: str):
    embed = [
        {
            "title": f"{title}",
            "description": "New Listing found!!",
            "keyword": keyword,
            "url": f"{mk_url}{vipUrl}",
            "color": 16711680,
            "fields": [
                {"name": "id", "value": f"{id}"},
                {"name": "url", "value": f"{mk_url}{vipUrl}"},
                {"name": "keyword", "value": keyword},
                {"name": "price", "value": str(price)},
            ],
            "image": {"url": image},
        }
    ]

    payload = {"embeds": embed}
    print(payload)

    for url in webhook_urls:
        try:
            r = httpx.post(url, json=payload)
            if r.status_code == 204:
                print("successfully notified")
            else:
                print("Failed to notify", r.status_code)
                print(r.json())
        except httpx.RequestError as e:
            print(e)
