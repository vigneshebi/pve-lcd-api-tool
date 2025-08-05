from .utils import parse_resp, save_to_csv_dynamic
from .api_client import get_client

PROJECT_NAME = "pve_lcd"
CSV_FILENAME = "bucket_list.csv"

CANDIDATE_PATHS = [
    f"{PROJECT_NAME}/api/Bucket/List",
    "api/Bucket/List",
    f"{PROJECT_NAME}/api/Sightings",
    "api/Sightings",
]

def main():
    getter = get_client()
    print("Trying CRequestsNga with corrected relative paths (no 'Failure/' prefix).")

    last_status = None
    last_body_preview = ""
    for rel in CANDIDATE_PATHS:
        print(f"GET {rel}")
        try:
            resp = getter(rel)
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
                for k in ("items", "value", "results", "data"):
                    if k in data and isinstance(data[k], list):
                        save_to_csv_dynamic(data[k], CSV_FILENAME)
                        break
                else:
                    save_to_csv_dynamic([data], CSV_FILENAME)
            else:
                print("Unexpected JSON shape; CSV not written.")
            return

    print("No candidate path returned 200.")
    if last_status is not None:
        print(f"[diag] Last status={last_status}; body preview: {last_body_preview}")
    print("Most likely cause: passing a path that duplicates the client's base.")

if __name__ == "__main__":
    main()
