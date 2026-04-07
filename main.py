import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone

from filter_out import FILTER_OUT

TUNNEL = "tunnel"
TUNNEL_CLASSES = [
"heated mat pilates",
"heated reformer full body burn",
"heated reformer sculpt & stretch",
"reformer full body burn",
]
TARGET_NAMES = [
    "sweat for a cause",
    "train",
    "teach",
    " x ",
    "with",
    "sweat for a cause/by donation",
    "sweat",
    "x",
    "+",
    "-",
    "—",
]



def is_free_class(class_data) -> bool:
    return class_data.get("is_free_class")


def is_sponsored_class(class_data, studio_name) -> bool:

    name = class_data.get("name").lower().strip()
    # Tunnel has different naming conventions
    if studio_name.lower() == TUNNEL:
        return name not in TUNNEL_CLASSES

    if "happy hour" in name:
        name = name.replace("happy hour", "").strip()
        name = name.strip("-").strip()

    if "mid-day" in name:
        name = name.replace("mid-day", "").strip()

    if any(target == name for target in FILTER_OUT):
        return False
    return any(target in name for target in TARGET_NAMES)

def format_date(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%Y-%m-%d %H:%M")

def format_time(time_str):
    return time_str[:5]

async def fetch(session, url):
    """Fetch a single URL and return JSON if possible."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


async def fetch_studio_data(studios: dict, days=45):
    """Fetch data from multiple studios for the next N days."""
    today = datetime.now(timezone.utc).date()
    SPECIAL_CLASSES = []
    SPONSORED_CLASSES = []
    interval = 10

    async with aiohttp.ClientSession() as session:
        tasks = []
        meta = []

        for studio_name, base_url in studios.items():
            if studio_name in ["Lagree West", "Jaybird"]:
                interval = 5
            for day_offset in range(0, days, interval):
                min_date = today + timedelta(days=day_offset)
                max_date = min_date + timedelta(days=4)  # 5-day span (inclusive)

                min_date_str = min_date.strftime("%Y-%m-%d")
                max_date_str = max_date.strftime("%Y-%m-%d")

                url = f"{base_url}&min_start_date={min_date_str}&max_start_date={max_date_str}"
                tasks.append(fetch(session, url))
                meta.append(studio_name)

        responses = await asyncio.gather(*tasks)

    # Process responses
    for (studio_name), data in zip(meta, responses):
        if not data:
            continue

        # Assuming the API returns {"classes": [...]}
        for cls in data.get("results", []):
            record = {
                "studio": studio_name,
                "name": cls.get("name"),
                "booking_start_date": format_date(cls.get("booking_start_datetime")),
                "location": cls.get("location", {}).get("name"),
                "start_date": cls.get("start_date"),
                "start_time": format_time(cls.get("start_time")),
                "available_spot_count": cls.get("available_spot_count"),
                "capacity": cls.get("capacity"),
            }

            if is_free_class(cls):
                SPECIAL_CLASSES.append(record)
            if is_sponsored_class(cls, studio_name):
                SPONSORED_CLASSES.append(record)

    return SPECIAL_CLASSES, SPONSORED_CLASSES


