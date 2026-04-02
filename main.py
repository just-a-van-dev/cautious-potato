import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
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

FILTER_OUT = ["advanced with headsets",
              "advanced (min 30 classes) with headsets",
              "advanced class with headsets",
              "advanced with headsets",
              "advanced workout with headsets",
              "advanced with headsets (min 30 classes)",
              "ass & abs with headsets",
              "ass & abs class with headsets",
              "ass and abs with headsets",
              "ass and abs class with headsets",
              "ass and abs workout with headsets",
              "beginners class with headsets",
              "booty + abs",
              "booty + core",
              "breathwork | one-on-one session",
              "charge x (hybrid strength + cardio)",
              "define x (strength full body)",
              "full body class with headsets",
              "full body workout with headsets",
              "full body with headsets",
              "foundation ( pilates + balance + core )",
              "foundation (pilates + balance + core)",
              "Happy Hour Mega Cardio Xpress- Arms/Abs+Tread (45)"
              "haus party - megaformer fullbody",
              "hiit + heavy",
              "hustle x",
              "infrared lagree - arms + core",
              "infrared lagree - legs + core",
              "infrared lagree - stretch + reset",
              "infrared lagree - full body",
              "intermediate (min 10 classes) with headsets",
              "lagree - arms + core",
              "lagree - full body",
              "lagree - fundamentals",
              "lagree - legs + core",
              "mat werk + weights",
              "mcx - ass/abs+tread",
              "mcx-arms/abs+tread",
              "mega cardio xpress",
              "mega cardio xpress- ass/abs+tread (45 min)",
              "mega cardio xpress- ass/abs+tread (45)",
              "mega cardio xpress- arms/abs+tread (45 min)",
              "mega cardio xpress- arms/abs+tread (45)",
              "mega cardio- arms/abs+tread",
              "mega cardio- arms/abs+tread (55 min)",
              "mega cardio- ass/abs+tread (55 min)",
              "megaformer ass + abs",
              "megaformer arms + abs",
              "megaformer strength + stretch",
              "megaformer strength + stretch (45 min)",
              "megaformer x flashback fridays",
              "megaformer + stretch",
              "meta + mat werk 45",
              "meta + mat werk 60 min",
              "meta + weights 45",
              "meta x mn",
              "postpartum +baby: control + core",
              "postpartum +baby: strength",
              "prenatal pilates + core",
              "reiki | one-on-one session",
              "ritual sound journey (relax and unwind)",
              "sculpt x (strength lower body + core)",
              "slow flow + sound",
              "slow flow vinyasa + sound",
              "sweatcon",
              "sweatcon arms + abs",
              "the balance + breathwork",
              "the balance + sound bath",
              "the balance x all is well",
              "the balance —",
              "the bird —",
              "the booty — reformer",
              "the burn | arms + abs —",
              "the burn | arms + abs — reformer —",
              "the burn | arms + abs — reformer (heated) — hh",
              "the burn — reformer (heated)",
              "the burn — reformer (heated) —",
              "the burn — reformer",
              "the burn — reformer —",
              "the build —",
              "the build -",
              "the burn —",
              "the impact (boxing technique & strength)",
              "the remix (rhythmic boxing & endurance)",
              "theme: rise + rave",
              "trx strength",
              "thrive (pilates + sculpt + light cardio)",
              "upper body + abs",
              "vinyasa slow flow yoga + sound",
              "warm yin + aromatherapy",
              "warm yin yoga + aromatherapy",
              "yin yoga + aromatherapy",
              "yoga | yin + aromatherapy",
              "yoga | candlelight yin + sound (warm)",
              "yoga | flow + yin (heated)"
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

    async with aiohttp.ClientSession() as session:
        tasks = []
        meta = []

        for studio_name, base_url in studios.items():
            for day_offset in range(0, days, 5):
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


