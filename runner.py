import json
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from main import fetch_studio_data

studio_base_urls = {
    "Lagree West": "https://lagreewest.marianatek.com/api/customer/v1/classes?format=json&location=48717,48721,48719,48720&region=48541&page_size=500",
    "Jaybird": "https://jaybird.marianatek.com/api/customer/v1/classes?page_size=500&location=48717,48784&region=48541&page_size=500",
    "Lagree Studio": "https://lagreestudio.marianatek.com/api/customer/v1/classes?page_size=500&location=48717&region=48541",
    "Ritual": "https://ritualurbanretreat.marianatek.com/api/customer/v1/classes?page_size=500&location=48717&region=48541",
    "Hustle": "https://hustleup.marianatek.com/api/customer/v1/classes?page_size=500&location=48717&region=48541",
    "Turf": "https://ourturf.marianatek.com/api/customer/v1/classes?page_size=500&location=48717&region=48541",
    "Spin Society": "https://spinsociety-hustle.marianatek.com/api/customer/v1/classes?page_size=500&location=48719&region=48541",
    "Lagree Pulse": "https://lagreepulse.marianatek.com/api/customer/v1/classes?page_size=500&location=48717&region=48541",
    "Evolution": "https://evolutionfitness.marianatek.com/api/customer/v1/classes?page_size=500&location=48717&region=48541"
}

result = asyncio.run(fetch_studio_data(studio_base_urls, days=45))
pacific = ZoneInfo("America/Vancouver")
json_data = {
    "last_updated": datetime.now(pacific).isoformat(),
    "special": result[0],
    "sponsored": result[1]
}

# make sure public/ exists
import os
os.makedirs("docs", exist_ok=True)

with open("docs/data.json", "w") as f:
    json.dump(json_data, f, indent=2)