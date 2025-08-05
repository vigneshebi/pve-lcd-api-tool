try:
    from CRequestsNga import CRequestsNga
except ImportError as e:
    raise SystemExit("Could not import CRequestsNga. Ensure it's installed / on PYTHONPATH.") from e

def get_client():
    client = CRequestsNga()
    getter = getattr(client, "Get", None)
    if not getter:
        raise SystemExit("This CRequestsNga build has no 'Get' method.")
    return getter
