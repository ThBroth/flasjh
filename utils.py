import re
import os
import json
from datetime import datetime, timedelta


def exportjson(content, filename):
    os.makedirs("data", exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(f"data/fb_{filename}_{now}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)
    return output_file

def is_json(data):
    try:
        json.loads(data)
        return True
    except ValueError:
        return False

def parse_post_datetime(inputTime):
    post_time = inputTime.get_text(strip=True)
    if ',' in post_time:
        time_str = post_time.split(',')[1].strip()

    date = None
    time = time_str.split('#')[0].strip() if '#' in time_str else time_str.strip()
    heading_text = inputTime.get_text(strip=True)

    if "Igår" in heading_text:
        yesterday = datetime.now() - timedelta(days=1)
        date = yesterday.strftime('%Y-%m-%d')
    elif "Idag" in heading_text:
        date = datetime.now().strftime('%Y-%m-%d')
    else:
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', heading_text)
        if date_match:
            date = date_match.group(0)

    return date, time
