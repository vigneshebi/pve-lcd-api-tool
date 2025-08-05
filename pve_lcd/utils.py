import json
import csv

def parse_resp(resp):
    status = getattr(resp, "status_code", None)
    text = getattr(resp, "text", "")
    data = None
    if hasattr(resp, "json"):
        try:
            data = resp.json()
        except Exception:
            data = None
    if data is None and isinstance(text, str):
        try:
            data = json.loads(text)
        except Exception:
            data = None
    return status, text, data

def save_to_csv_dynamic(rows, csv_path: str):
    if not isinstance(rows, list) or not rows:
        print("No data to write.")
        return
    keys = set()
    for r in rows:
        if isinstance(r, dict):
            keys.update(r.keys())
    headers = sorted(keys)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f" Saved {len(rows)} rows to '{csv_path}'")
