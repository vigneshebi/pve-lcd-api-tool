

import json
import csv

PROJECT_NAME = "pve_lcd"
CSV_FILENAME = "bucket_list.csv"


CANDIDATE_PATHS = [
    f"{PROJECT_NAME}/api/Bucket/List",  
    "api/Bucket/List",                  
    f"{PROJECT_NAME}/api/Sightings",    
    "api/Sightings",
]

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

def main():
    try:
        from CRequestsNga import CRequestsNga
    except ImportError as e:
        raise SystemExit("Could not import CRequestsNga. Ensure it's installed / on PYTHONPATH.") from e

    client = CRequestsNga()
    getter = getattr(client, "Get", None)
    if not getter:
        raise SystemExit("This CRequestsNga build has no 'Get' method.")

    print("Trying CRequestsNga with corrected relative paths (no 'Failure/' prefix).")

    last_status = None
    last_body_preview = ""
    for rel in CANDIDATE_PATHS:
        print(f"GET {rel}")
        try:
            resp = getter(rel)  # no headers; client handles auth internally
        except TypeError as te:
            print(f"Get signature error on '{rel}': {te}")
            continue
        except Exception as e:
            print(f"Failed to send '{rel}': {e}")
            continue

        status, text, data = parse_resp(resp)
        last_status = status
        last_body_preview = (text or "")[:400]
        print(f"   ↳ status={status}")

        if status == 200:
            print("NGA call successful.")
            if isinstance(data, list):
                save_to_csv_dynamic(data, CSV_FILENAME)
            elif isinstance(data, dict):
                # unwrap common list containers
                for k in ("items", "value", "results", "data"):
                    if k in data and isinstance(data[k], list):
                        save_to_csv_dynamic(data[k], CSV_FILENAME)
                        break
                else:
                    save_to_csv_dynamic([data], CSV_FILENAME)
            else:
                print("Unexpected JSON shape; CSV not written.")
            return

    # If none of the candidates worked, report the last status/body snippet
    print("No candidate path returned 200.")
    if last_status is not None:
        print(f"[diag] Last status={last_status}; body preview: {last_body_preview}")
    print("Most likely cause: passing a path that duplicates the client's base.")
    print("   Your client’s base appears to be '/Failure', so pass 'pve_lcd/api/Bucket/List' (without 'Failure/').")

if __name__ == "__main__":
    main()
