from datetime import datetime

import requests

def get_alo_events():
    url = "https://wellnessclub.aloyoga.com/api/v2/events?sections=upcoming&country=CA&timezone=America/Los_Angeles"
    response = requests.get(url)
    result = response.json().get("upcoming",{}).get("data",[])
    alo_event = []
    for r in result:
        s = r["start_at"]

        dt = datetime.fromisoformat(s)

        date = dt.strftime("%Y-%m-%d")
        time = dt.strftime("%H:%M")
        alo_event.append(
            {
                "studio": "Alo",
                "name": r["title"],
                "booking_start_date": "Open to book" if r["registration_open"] else "Not Open to book",
                "location": r["city"],
                "start_date": date,
                "start_time": time,
                "available_spot_count": r["spots_remaining"],
                "capacity": r["used_slots"],
            }
        )
    return alo_event