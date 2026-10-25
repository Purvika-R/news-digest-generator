import re


def parse_interests(text, limit=8):
    """Comma-separated interests, duplicates removed, capped at `limit`."""
    items = [x.strip() for x in re.split(r"[,\n]", text or "") if x.strip()]
    unique = list(dict.fromkeys(items))
    if len(unique) > limit:
        raise ValueError(f"Choose up to {limit} interests.")
    return unique
